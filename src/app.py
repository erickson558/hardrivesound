"""
Aplicación principal del simulador de disco duro.
Integra backend y frontend para crear la aplicación completa.
"""
import sys
import os
import threading
import traceback
from typing import Optional
from src.utils.logger import logger
from src.utils.constants import APP_NAME, APP_VERSION
from src.models.config_model import AppConfig
from src.backend.config_manager import ConfigManager
from src.backend.audio_engine import AudioEngine
from src.backend.disk_monitor import DiskMonitor
from src.frontend.tray_interface import TrayInterface
from src.frontend.settings_window import SettingsWindow


class HardDriveSimulator:
    """Clase principal del simulador de disco duro"""
    
    def __init__(self):
        """Inicializar el simulador"""
        try:
            logger.info(f"Inicializando {APP_NAME} v{APP_VERSION}...")
            self._is_quitting = False
            
            # Determinar si está compilado
            self.is_compiled = getattr(sys, 'frozen', False)
            self.base_dir = self._get_base_dir()
            logger.info(f"Modo: {'Compilado' if self.is_compiled else 'Desarrollo'}")
            logger.info(f"Directorio: {self.base_dir}")
            
            # Componentes del backend
            self.config_manager = ConfigManager(self.base_dir)
            self.config = self.config_manager.load_config()
            
            self.audio_engine = AudioEngine(self.base_dir, self.config)
            self.audio_engine.check_sound_files()
            
            self.disk_monitor = DiskMonitor(self.config.icon_behavior)
            
            # Componente del frontend
            self.tray_interface = TrayInterface(self.is_compiled, self.base_dir)
            self.tray_interface.set_config(self.config)
            self.settings_window = SettingsWindow(
                self.config_manager,
                self.disk_monitor,
                self.tray_interface,
            )
            
            # Conectar callbacks
            self._setup_callbacks()
            
            # Inicializar UI
            self.tray_interface.initialize()
            self._hide_console()
            
            logger.info("✅ Simulador inicializado correctamente")
            
        except Exception as e:
            logger.error(f"❌ ERROR CRÍTICO en inicialización: {e}")
            logger.error(traceback.format_exc())
            raise
    
    def _get_base_dir(self) -> str:
        """Obtener directorio base de la aplicación"""
        if self.is_compiled:
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    def _hide_console(self) -> None:
        """Ocultar ventana de consola en Windows"""
        try:
            import ctypes
            ctypes.windll.user32.ShowWindow(
                ctypes.windll.kernel32.GetConsoleWindow(), 0
            )
            logger.info("✅ Consola ocultada")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo ocultar la consola: {e}")
    
    def _setup_callbacks(self) -> None:
        """Configurar callbacks entre componentes"""
        # Callbacks del monitor de disco
        self.disk_monitor.set_activity_callback(self._on_disk_activity)
        self.disk_monitor.set_icon_update_callback(self._on_icon_update)
        
        # Callbacks de la interfaz
        self.tray_interface.on_toggle_global_sound = self._handle_toggle_global_sound
        self.tray_interface.on_toggle_sound_type = self._handle_toggle_sound_type
        self.tray_interface.on_toggle_sound_trigger = self._handle_toggle_sound_trigger
        self.tray_interface.on_change_delay = self._handle_change_delay
        self.tray_interface.on_change_icon_behavior = self._handle_change_icon_behavior
        self.tray_interface.on_change_icon_style = self._handle_change_icon_style
        self.tray_interface.on_change_language = self._handle_change_language
        self.tray_interface.on_open_settings = self._handle_open_settings
        self.tray_interface.on_quit = self.quit
    
    def _on_disk_activity(self, activity_type: str) -> None:
        """
        Callback para actividad del disco.
        
        Args:
            activity_type: Tipo de actividad detectada
        """
        self.audio_engine.play_sound_by_type(activity_type)
        self.tray_interface.increment_activity_count()
    
    def _on_icon_update(self, activity_type: str) -> None:
        """
        Callback para actualización del icono.
        
        Args:
            activity_type: Tipo de actividad para el icono
        """
        self.tray_interface.update_icon_color(activity_type)
        self.tray_interface.process_pending_updates()
    
    def _handle_toggle_global_sound(self) -> None:
        """Manejar toggle de sonido global"""
        new_state = self.config_manager.toggle_global_sound()
        status = 'ACTIVADO' if new_state else 'DESACTIVADO'
        logger.info(f"🔊 Sonido global: {status}")
    
    def _handle_toggle_sound_type(self, sound_type: str) -> None:
        """Manejar toggle de tipo de sonido"""
        new_state = self.config_manager.toggle_sound_type(sound_type)
        status = 'activado' if new_state else 'desactivado'
        logger.info(f"🔊 Sonido {sound_type}: {status}")
    
    def _handle_toggle_sound_trigger(self, trigger_type: str) -> None:
        """Manejar toggle de trigger"""
        new_state = self.config_manager.toggle_sound_trigger(trigger_type)
        status = 'activado' if new_state else 'desactivado'
        logger.info(f"🔊 Trigger {trigger_type}: {status}")
    
    def _handle_change_delay(self) -> None:
        """Manejar cambio de delay"""
        new_delay = self.config_manager.change_global_delay()
        logger.info(f"⏱️ Nuevo delay: {new_delay}s")
    
    def _handle_change_icon_behavior(self) -> None:
        """Manejar cambio de comportamiento de icono"""
        new_behavior = self.config_manager.change_icon_behavior()
        self.disk_monitor.set_icon_behavior(new_behavior)
        logger.info(f"🎨 Comportamiento de icono: {new_behavior}")
    
    def _handle_change_icon_style(self, new_style: str) -> None:
        """Manejar cambio de estilo de icono"""
        logger.info(f"🖼️ Estilo de icono: {new_style}")

    def _handle_change_language(self) -> None:
        """Manejar cambio de idioma"""
        new_language = self.config_manager.change_language()
        self.tray_interface.set_language(new_language)
        logger.info(f"🌍 Idioma: {new_language}")

    def _handle_open_settings(self) -> None:
        """Abrir panel GUI de configuración."""
        self.settings_window.open_window()
    
    def start(self) -> None:
        """Iniciar la aplicación"""
        logger.info("🚀 Iniciando aplicación...")
        
        try:
            # Iniciar thread de monitoreo
            monitor_thread = threading.Thread(
                target=self.disk_monitor.monitor_loop,
                daemon=True
            )
            monitor_thread.start()
            logger.info("✅ Thread de monitoreo iniciado")
            
            # Iniciar interfaz (bloqueante)
            self.tray_interface.run()
            
        except Exception as e:
            logger.error(f"❌ ERROR en ejecución: {e}")
            logger.error(traceback.format_exc())
        finally:
            self.quit()
    
    def quit(self) -> None:
        """Salir de la aplicación"""
        if self._is_quitting:
            return

        self._is_quitting = True
        logger.info("⏹️ Cerrando aplicación...")
        
        try:
            self.disk_monitor.stop()
            self.audio_engine.stop()
            self.config_manager.save_config()
            self.tray_interface.stop()
            logger.info("✅ Aplicación cerrada correctamente")
        except Exception as e:
            logger.error(f"❌ Error al cerrar: {e}")


def global_exception_handler(exc_type, exc_value, exc_traceback):
    """Manejador global de excepciones"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger.critical("❌ EXCEPCIÓN NO CAPTURADA:")
    logger.critical("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))


# Configurar manejador global
sys.excepthook = global_exception_handler
