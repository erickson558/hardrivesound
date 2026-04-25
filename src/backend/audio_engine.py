"""
Motor de audio para reproducción de sonidos.
Maneja la reproducción de archivos de audio del sistema.
"""
import os
import time
import queue
import threading
import random
import winsound
from typing import Optional
from src.models.config_model import AppConfig
from src.backend.sound_synth import generate_missing_hdd_sounds, get_existing_variant_files
from src.utils.logger import logger
from src.utils.constants import ACTIVITY_TYPE_READ, ACTIVITY_TYPE_WRITE, ACTIVITY_TYPE_BOTH


class AudioEngine:
    """Motor de audio para reproducción de sonidos"""
    
    def __init__(self, base_dir: str, config: AppConfig):
        """
        Inicializar motor de audio.
        
        Args:
            base_dir: Directorio base de la aplicación
            config: Configuración de la aplicación
        """
        self.base_dir = base_dir
        self.config = config
        self.sound_cooldown_until = 0.0
        self._next_allowed_play = 0.0
        self._queue: queue.Queue = queue.Queue(maxsize=10)
        self._stop_event = threading.Event()
        self._aggressive_hdd_mode = False
        self._burst_chance_by_type = {
            ACTIVITY_TYPE_READ: 0.18,
            ACTIVITY_TYPE_WRITE: 0.10,
            ACTIVITY_TYPE_BOTH: 0.28,
        }

        # Reproducción serializada para evitar cortes por superposición.
        self._worker = threading.Thread(target=self._playback_loop, daemon=True)
        self._worker.start()
    
    def get_resource_path(self, filename: str) -> str:
        """
        Obtener ruta completa para un archivo de recurso.
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            Ruta completa al archivo
        """
        return os.path.join(self.base_dir, filename)
    
    def check_sound_files(self) -> dict:
        """
        Verificar disponibilidad de archivos de sonido.
        
        Returns:
            Diccionario con disponibilidad de cada sonido
        """
        logger.info("Verificando archivos de sonido...")

        # Si faltan sonidos por defecto, se sintetizan automaticamente.
        generate_missing_hdd_sounds(
            self.base_dir,
            variants=8,
            fade_profile=self.config.hdd_fade_profile,
        )

        availability = {}
        
        for sound_type, sound_config in self.config.sounds.items():
            sound_file_path = self.get_resource_path(sound_config.file)
            available = os.path.exists(sound_file_path)
            sound_config.available = available
            availability[sound_type] = available
            
            status = "✅ ENCONTRADO" if available else "❌ NO ENCONTRADO"
            logger.info(f"   {sound_config.file} - {status}")
        
        return availability
    
    def play_sound(self, filename: str) -> bool:
        """
        Reproducir un archivo de sonido.
        
        Args:
            filename: Nombre del archivo de sonido
            
        Returns:
            True si se reprodujo exitosamente
        """
        sound_file_path = self.get_resource_path(filename)
        
        try:
            if os.path.exists(sound_file_path):
                winsound.PlaySound(sound_file_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                logger.debug(f"🔊 Sonido reproducido: {filename}")
                return True
            else:
                logger.error(f"❌ Archivo no encontrado: {sound_file_path}")
        except Exception as e:
            logger.error(f"❌ Error reproduciendo sonido: {e}")
        
        return False

    def _playback_loop(self) -> None:
        """Consumir la cola de audio y reproducir en orden."""
        while not self._stop_event.is_set():
            try:
                filename = self._queue.get(timeout=0.25)
            except queue.Empty:
                continue

            if filename is None:
                break

            sound_file_path = self.get_resource_path(filename)
            try:
                if os.path.exists(sound_file_path):
                    winsound.PlaySound(sound_file_path, winsound.SND_FILENAME)
                    logger.debug(f"🔊 Sonido reproducido (serial): {filename}")
                else:
                    logger.error(f"❌ Archivo no encontrado: {sound_file_path}")
            except Exception as e:
                logger.error(f"❌ Error en cola de audio: {e}")
            finally:
                self._queue.task_done()

    def stop(self) -> None:
        """Detener hilo de reproducción de audio."""
        self._stop_event.set()
        try:
            self._queue.put_nowait(None)
        except queue.Full:
            pass

        if self._worker.is_alive():
            self._worker.join(timeout=0.6)

    def _is_synthetic_hdd_file(self, filename: str) -> bool:
        """
        Detectar sonidos HDD sinteticos (pequeños, generados internamente).
        Archivos reales grandes (>50 KB) NO se consideran sinteticos.
        """
        lower = filename.lower()
        if not (lower.startswith("hdd_") and lower.endswith(".wav")):
            return False
        # Archivos grandes son grabaciones reales, no sinteticos
        full_path = os.path.join(self.base_dir, filename)
        try:
            if os.path.exists(full_path) and os.path.getsize(full_path) > 50_000:
                return False
        except OSError:
            pass
        return True

    def _pick_sound_variant(self, filename: str) -> str:
        """
        Elegir variante aleatoria solo para sonidos sinteticos pequenos.
        Los archivos reales (grabaciones, >50 KB) se reproducen directamente.
        """
        if not self._is_synthetic_hdd_file(filename):
            # Archivo real o externo: reproducir sin variante
            return filename

        available = get_existing_variant_files(self.base_dir, filename, variants=8)
        if not available:
            return filename

        return random.choice(available)

    def _enqueue_file(self, filename: str) -> bool:
        """Encolar archivo de audio de forma segura y no bloqueante."""
        try:
            self._queue.put_nowait(filename)
            return True
        except queue.Full:
            logger.debug("Cola de audio llena, se descarta evento para mantener fluidez")
            return False
    
    def play_sound_by_type(self, sound_type: str) -> bool:
        """
        Reproducir sonido según tipo de actividad.
        
        Args:
            sound_type: Tipo de sonido (read, write, both)
            
        Returns:
            True si se reprodujo exitosamente
        """
        # Verificar si el sonido global está habilitado
        if not self.config.enabled:
            return False
        
        # Verificar si el trigger está habilitado
        if sound_type == ACTIVITY_TYPE_READ and not self.config.sound_triggers.read:
            return False
        if sound_type == ACTIVITY_TYPE_WRITE and not self.config.sound_triggers.write:
            return False
        if sound_type == ACTIVITY_TYPE_BOTH and not self.config.sound_triggers.both:
            return False
        
        # Verificar si el sonido específico existe y está habilitado
        if sound_type not in self.config.sounds:
            return False
        
        sound_config = self.config.sounds[sound_type]
        if not sound_config.enabled or not sound_config.available:
            return False
        
        now = time.time()

        # Verificar cooldown y ritmo mínimo para reducir saturación.
        if now < self.sound_cooldown_until or now < self._next_allowed_play:
            return False

        file_to_play = self._pick_sound_variant(sound_config.file)

        # Determinar si el archivo es un sonido sintetico pequeno o una grabacion real.
        is_synthetic = self._is_synthetic_hdd_file(sound_config.file)

        # Cooldown: sinteticos usan ritmo rapido; archivos reales respetan global_delay.
        if is_synthetic:
            effective_cooldown = min(self.config.global_delay, 0.16)
        else:
            effective_cooldown = self.config.global_delay

        # Encolar en vez de reproducir directo evita cortes por solapamiento.
        try:
            if not self._enqueue_file(file_to_play):
                return False

            self.sound_cooldown_until = now + max(0.03, effective_cooldown)

            if is_synthetic:
                # Para sinteticos, agregar variacion temporal para sonar organico.
                self._next_allowed_play = now + random.uniform(0.03, 0.09)
                # Micro-rafagas opcionales para modo agresivo (solo sinteticos).
                if self._aggressive_hdd_mode:
                    burst_chance = self._burst_chance_by_type.get(sound_type, 0.2)
                    if random.random() < burst_chance:
                        burst_source = "hdd_click.wav" if sound_type != ACTIVITY_TYPE_WRITE else sound_config.file
                        burst_file = self._pick_sound_variant(burst_source)
                        self._enqueue_file(burst_file)
            else:
                # Para archivos reales, respetar el delay global configurado.
                self._next_allowed_play = now + max(0.08, self.config.global_delay * 0.5)

            logger.debug(f"✅ Sonido {sound_type} encolado")
            return True
        except queue.Full:
            logger.debug("Cola de audio llena, se descarta evento para mantener fluidez")
            return False
