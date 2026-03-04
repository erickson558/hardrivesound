"""
Gestor de configuración del simulador.
Maneja carga, guardado y actualización de la configuración.
"""
import json
import os
from typing import Optional
from src.models.config_model import AppConfig, SoundConfig
from src.utils.logger import logger
from src.utils.constants import CONFIG_FILE


class ConfigManager:
    """Gestor de configuración de la aplicación"""
    
    def __init__(self, base_dir: str):
        """
        Inicializar gestor de configuración.
        
        Args:
            base_dir: Directorio base de la aplicación
        """
        self.base_dir = base_dir
        self.config_file = os.path.join(base_dir, CONFIG_FILE)
        self.config: AppConfig = AppConfig()
    
    def load_config(self) -> AppConfig:
        """
        Cargar configuración desde archivo.
        
        Returns:
            Configuración de la aplicación
        """
        logger.info(f"Cargando configuración desde: {self.config_file}")
        
        try:
            if os.path.exists(self.config_file):
                logger.info("✅ Archivo config.json encontrado")
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.config = AppConfig.from_dict(data)
                    logger.info(f"✅ Configuración cargada (v{self.config.version})")
            else:
                logger.warning("⚠️ config.json no encontrado, usando defaults")
                self.config = AppConfig()
                self.save_config()
        except Exception as e:
            logger.error(f"❌ Error cargando configuración: {e}")
            self.config = AppConfig()
        
        return self.config
    
    def save_config(self) -> bool:
        """
        Guardar configuración en archivo.
        
        Returns:
            True si se guardó exitosamente
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config.to_dict(), f, indent=4, ensure_ascii=False)
            logger.info(f"✅ Configuración guardada en: {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"❌ Error guardando configuración: {e}")
            return False
    
    def update_sound_availability(self, sound_type: str, available: bool) -> None:
        """
        Actualizar disponibilidad de un sonido.
        
        Args:
            sound_type: Tipo de sonido (read, write, both)
            available: Si el archivo está disponible
        """
        if sound_type in self.config.sounds:
            self.config.sounds[sound_type].available = available
    
    def toggle_global_sound(self) -> bool:
        """
        Alternar sonido global.
        
        Returns:
            Nuevo estado del sonido global
        """
        self.config.enabled = not self.config.enabled
        self.save_config()
        return self.config.enabled
    
    def toggle_sound_type(self, sound_type: str) -> bool:
        """
        Alternar un tipo de sonido específico.
        
        Args:
            sound_type: Tipo de sonido (read, write, both)
            
        Returns:
            Nuevo estado del sonido
        """
        if sound_type in self.config.sounds:
            self.config.sounds[sound_type].enabled = not self.config.sounds[sound_type].enabled
            self.save_config()
            return self.config.sounds[sound_type].enabled
        return False
    
    def toggle_sound_trigger(self, trigger_type: str) -> bool:
        """
        Alternar trigger de sonido.
        
        Args:
            trigger_type: Tipo de trigger (read, write, both)
            
        Returns:
            Nuevo estado del trigger
        """
        if trigger_type == 'read':
            self.config.sound_triggers.read = not self.config.sound_triggers.read
            new_state = self.config.sound_triggers.read
        elif trigger_type == 'write':
            self.config.sound_triggers.write = not self.config.sound_triggers.write
            new_state = self.config.sound_triggers.write
        elif trigger_type == 'both':
            self.config.sound_triggers.both = not self.config.sound_triggers.both
            new_state = self.config.sound_triggers.both
        else:
            return False
        
        self.save_config()
        return new_state
    
    def change_global_delay(self) -> float:
        """
        Cambiar delay global (cicla entre valores predefinidos).
        
        Returns:
            Nuevo valor de delay
        """
        from src.utils.constants import AVAILABLE_DELAYS
        
        current = self.config.global_delay
        current_index = AVAILABLE_DELAYS.index(current) if current in AVAILABLE_DELAYS else 1
        new_index = (current_index + 1) % len(AVAILABLE_DELAYS)
        self.config.global_delay = AVAILABLE_DELAYS[new_index]
        self.save_config()
        return self.config.global_delay
    
    def change_icon_behavior(self) -> str:
        """
        Cambiar comportamiento del icono (cicla entre opciones).
        
        Returns:
            Nuevo comportamiento
        """
        from src.utils.constants import ICON_BEHAVIORS
        
        current = self.config.icon_behavior
        current_index = ICON_BEHAVIORS.index(current) if current in ICON_BEHAVIORS else 0
        new_index = (current_index + 1) % len(ICON_BEHAVIORS)
        self.config.icon_behavior = ICON_BEHAVIORS[new_index]
        self.save_config()
        return self.config.icon_behavior
