"""
Motor de audio para reproducción de sonidos.
Maneja la reproducción de archivos de audio del sistema.
"""
import os
import time
import winsound
from typing import Optional
from src.models.config_model import AppConfig
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
        
        # Verificar cooldown
        if time.time() < self.sound_cooldown_until:
            return False
        
        # Reproducir sonido
        success = self.play_sound(sound_config.file)
        
        if success:
            self.sound_cooldown_until = time.time() + self.config.global_delay
            logger.debug(f"✅ Sonido {sound_type} reproducido")
        
        return success
