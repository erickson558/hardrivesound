"""
Interfaz de bandeja del sistema.
Maneja el icono y menú en la bandeja del sistema.
"""
import time
import platform
from typing import Optional, Callable
from src.utils.logger import logger
from src.utils.constants import (
    APP_NAME, APP_VERSION, APP_AUTHOR, APP_YEAR, APP_DESCRIPTION,
    STATUS_READING, STATUS_WRITING, STATUS_BOTH, STATUS_INACTIVE,
    ICON_STYLES, ACTIVITY_TYPE_READ, ACTIVITY_TYPE_WRITE, 
    ACTIVITY_TYPE_BOTH, ACTIVITY_TYPE_INACTIVE
)
from src.frontend.icon_generator import IconGenerator

try:
    from pystray import Icon, Menu, MenuItem
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False
    logger.error("❌ pystray no disponible")


class TrayInterface:
    """Interfaz de bandeja del sistema"""
    
    def __init__(self, is_compiled: bool = False, base_dir: str = ""):
        """
        Inicializar interfaz de bandeja.
        
        Args:
            is_compiled: Si la app está compilada como .exe
            base_dir: Directorio base de la aplicación
        """
        self.is_compiled = is_compiled
        self.base_dir = base_dir
        self.tray_icon: Optional[Icon] = None
        self.icon_style = 'modern'
        self.current_status = STATUS_INACTIVE
        self.activity_count = 0
        self.start_time = time.time()
        self.menu_update_pending = False
        
        # Callbacks
        self.on_toggle_global_sound: Optional[Callable] = None
        self.on_toggle_sound_type: Optional[Callable] = None
        self.on_toggle_sound_trigger: Optional[Callable] = None
        self.on_change_delay: Optional[Callable] = None
        self.on_change_icon_behavior: Optional[Callable] = None
        self.on_change_icon_style: Optional[Callable] = None
        self.on_quit: Optional[Callable] = None
        
        # Configuración de referencia (se actualizará externamente)
        self.config = None
        
        if not PYSTRAY_AVAILABLE:
            logger.error("❌ TrayInterface no puede funcionar sin pystray")
    
    def set_config(self, config) -> None:
        """Establecer referencia a configuración"""
        self.config = config
    
    def create_icons(self) -> None:
        """Crear todos los iconos necesarios"""
        logger.info("Creando iconos de bandeja...")
        generator = IconGenerator(self.icon_style)
        
        self.idle_icon = generator.create_icon("gray")
        self.read_icon = generator.create_icon("green")
        self.write_icon = generator.create_icon("red")
        self.both_icon = generator.create_icon("green")
        
        logger.info("✅ Iconos creados")
    
    def change_icon_style(self) -> str:
        """
        Cambiar estilo de iconos.
        
        Returns:
            Nuevo estilo
        """
        current_index = ICON_STYLES.index(self.icon_style)
        new_index = (current_index + 1) % len(ICON_STYLES)
        self.icon_style = ICON_STYLES[new_index]
        
        # Recrear iconos
        self.create_icons()
        logger.info(f"🎨 Estilo cambiado a: {self.icon_style}")
        
        return self.icon_style
    
    def update_icon_color(self, activity_type: str) -> None:
        """
        Actualizar color del icono según actividad.
        
        Args:
            activity_type: Tipo de actividad (read, write, both, inactive)
        """
        try:
            if activity_type == ACTIVITY_TYPE_READ:
                self.tray_icon.icon = self.read_icon
                self.current_status = STATUS_READING
            elif activity_type == ACTIVITY_TYPE_WRITE:
                self.tray_icon.icon = self.write_icon
                self.current_status = STATUS_WRITING
            elif activity_type == ACTIVITY_TYPE_BOTH:
                self.tray_icon.icon = self.both_icon
                self.current_status = STATUS_BOTH
            else:
                self.tray_icon.icon = self.idle_icon
                self.current_status = STATUS_INACTIVE
            
            self.schedule_menu_update()
            logger.debug(f"Icono actualizado: {self.current_status}")
        except Exception as e:
            logger.error(f"❌ Error actualizando icono: {e}")
    
    def schedule_menu_update(self) -> None:
        """Programar actualización del menú"""
        self.menu_update_pending = True
    
    def process_pending_updates(self) -> None:
        """Procesar actualizaciones pendientes del menú"""
        if self.menu_update_pending:
            self.menu_update_pending = False
            self.update_menu()
    
    def increment_activity_count(self) -> None:
        """Incrementar contador de actividades"""
        self.activity_count += 1
    
    def get_uptime(self) -> str:
        """
        Obtener tiempo de actividad formateado.
        
        Returns:
            Tiempo en formato HH:MM:SS
        """
        uptime = time.time() - self.start_time
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def show_about_info(self) -> None:
        """Mostrar información 'Acerca de'"""
        about_text = f"""
╔══════════════════════════════════════════════════╗
║             {APP_NAME}             ║
╠══════════════════════════════════════════════════╣
║  Versión: {APP_VERSION}                            ║
║  Modo: {'Compilado (.exe)' if self.is_compiled else 'Script (.py)'}                  ║
║  Estilo: {self.icon_style.title()}                            ║
║                                                    ║
║  Autor: {APP_AUTHOR}                             ║
║  Año: {APP_YEAR}                                ║
║  Licencia: Apache-2.0                             ║
║                                                    ║
║  Descripción:                                     ║
║  {APP_DESCRIPTION}    ║
║                                                    ║
║  Características:                                  ║
║  • Monitorización en tiempo real                  ║
║  • Sonidos vintage personalizables                ║
║  • 4 estilos de icono diferentes                  ║
║  • Configuración persistente                      ║
║                                                    ║
║  Sistema:                                         ║
║  • Python {platform.python_version()}                           ║
║  • {platform.system()} {platform.release()}                    ║
║  • Tiempo activo: {self.get_uptime()}                    ║
║  • Actividades: {self.activity_count}                       ║
╚══════════════════════════════════════════════════╝
"""
        logger.info(f"Información 'Acerca de':\n{about_text}")
    
    def create_menu_action(self, action_function: Callable, *args) -> Callable:
        """
        Crear una acción de menú que programa actualización.
        
        Args:
            action_function: Función a ejecutar
            *args: Argumentos para la función
            
        Returns:
            Función envuelta para el menú
        """
        def menu_action(icon, item):
            try:
                action_function(*args)
                self.schedule_menu_update()
            except Exception as e:
                logger.error(f"❌ Error en acción de menú: {e}")
        return menu_action
    
    def build_menu(self) -> Menu:
        """
        Construir menú de la bandeja.
        
        Returns:
            Menú construido
        """
        if not self.config:
            return Menu(
                MenuItem('⚠️ Sin configuración', None, enabled=False),
                MenuItem('❌ Salir', lambda i, _: self.on_quit() if self.on_quit else None)
            )
        
        # Estados
        global_sound_text = f'🔊 Global: {"ON" if self.config.enabled else "OFF"}'
        delay_text = f'⏱️ Delay: {self.config.global_delay}s'
        behavior_text = f'🎨 Icono: {self.config.icon_behavior.replace("_", " ").title()}'
        style_text = f'🖼️ Estilo: {self.icon_style.title()}'
        
        # Estados de sonidos
        read_status = "✅" if self.config.sounds['read'].enabled else "❌"
        write_status = "✅" if self.config.sounds['write'].enabled else "❌"
        both_status = "✅" if self.config.sounds['both'].enabled else "❌"
        
        # Estados de triggers
        read_trigger = "🔊" if self.config.sound_triggers.read else "🔇"
        write_trigger = "🔊" if self.config.sound_triggers.write else "🔇"
        both_trigger = "🔊" if self.config.sound_triggers.both else "🔇"
        
        # Icono de estado
        status_icons = {
            STATUS_READING: "🟢",
            STATUS_WRITING: "🔴",
            STATUS_BOTH: "🟡",
            STATUS_INACTIVE: "⚫"
        }
        status_icon = status_icons.get(self.current_status, "⚫")
        
        return Menu(
            MenuItem(f'💾 {APP_NAME}', None, enabled=False),
            MenuItem(f'📦 v{APP_VERSION}', None, enabled=False),
            MenuItem(f'🔧 {"EXE" if self.is_compiled else "PY"}', None, enabled=False),
            MenuItem(f'{status_icon} {self.current_status}', None, enabled=False),
            MenuItem(f'🎯 Actividades: {self.activity_count}', None, enabled=False),
            MenuItem('---', None, enabled=False),
            
            MenuItem('🎛️ CONFIGURACIÓN GLOBAL', None, enabled=False),
            MenuItem(global_sound_text, self.create_menu_action(self._handle_toggle_global)),
            MenuItem(delay_text, self.create_menu_action(self._handle_change_delay)),
            MenuItem(behavior_text, self.create_menu_action(self._handle_change_behavior)),
            MenuItem(style_text, self.create_menu_action(self._handle_change_style)),
            MenuItem('---', None, enabled=False),
            
            MenuItem('🔊 ACTIVAR SONIDO EN:', None, enabled=False),
            MenuItem(f'{read_trigger} Solo Lectura', self.create_menu_action(self._handle_toggle_trigger, 'read')),
            MenuItem(f'{write_trigger} Solo Escritura', self.create_menu_action(self._handle_toggle_trigger, 'write')),
            MenuItem(f'{both_trigger} Lectura+Escritura', self.create_menu_action(self._handle_toggle_trigger, 'both')),
            MenuItem('---', None, enabled=False),
            
            MenuItem('📖 SONIDOS INDIVIDUALES', None, enabled=False),
            MenuItem(f'{read_status} Sonido Lectura', self.create_menu_action(self._handle_toggle_sound, 'read')),
            MenuItem(f'{write_status} Sonido Escritura', self.create_menu_action(self._handle_toggle_sound, 'write')),
            MenuItem(f'{both_status} Sonido Ambos', self.create_menu_action(self._handle_toggle_sound, 'both')),
            MenuItem('---', None, enabled=False),
            
            MenuItem('ℹ️ Acerca de...', lambda i, _: self.show_about_info()),
            MenuItem('---', None, enabled=False),
            MenuItem('❌ Salir', lambda i, _: self.on_quit() if self.on_quit else None)
        )
    
    def _handle_toggle_global(self) -> None:
        """Manejar toggle de sonido global"""
        if self.on_toggle_global_sound:
            self.on_toggle_global_sound()
    
    def _handle_toggle_sound(self, sound_type: str) -> None:
        """Manejar toggle de tipo de sonido"""
        if self.on_toggle_sound_type:
            self.on_toggle_sound_type(sound_type)
    
    def _handle_toggle_trigger(self, trigger_type: str) -> None:
        """Manejar toggle de trigger"""
        if self.on_toggle_sound_trigger:
            self.on_toggle_sound_trigger(trigger_type)
    
    def _handle_change_delay(self) -> None:
        """Manejar cambio de delay"""
        if self.on_change_delay:
            self.on_change_delay()
    
    def _handle_change_behavior(self) -> None:
        """Manejar cambio de comportamiento de icono"""
        if self.on_change_icon_behavior:
            self.on_change_icon_behavior()
    
    def _handle_change_style(self) -> None:
        """Manejar cambio de estilo de icono"""
        new_style = self.change_icon_style()
        if self.on_change_icon_style:
            self.on_change_icon_style(new_style)
    
    def initialize(self) -> None:
        """Inicializar interfaz de bandeja"""
        if not PYSTRAY_AVAILABLE:
            logger.error("❌ No se puede inicializar - pystray no disponible")
            return
        
        logger.info("Inicializando interfaz de bandeja...")
        self.create_icons()
        
        menu = self.build_menu()
        self.tray_icon = Icon('hard_drive_simulator')
        self.tray_icon.title = f"{APP_NAME} v{APP_VERSION} - {self.current_status}"
        self.tray_icon.menu = menu
        self.tray_icon.icon = self.idle_icon
        
        logger.info("✅ Interfaz de bandeja inicializada")
    
    def update_menu(self) -> None:
        """Actualizar menú de la bandeja"""
        if self.tray_icon:
            self.tray_icon.menu = self.build_menu()
            self.tray_icon.title = f"{APP_NAME} v{APP_VERSION} - {self.current_status}"
            logger.debug("✅ Menú actualizado")
    
    def run(self) -> None:
        """Ejecutar bucle principal de la interfaz"""
        if self.tray_icon:
            logger.info("🚀 Iniciando bucle de interfaz de bandeja...")
            self.tray_icon.run()
    
    def stop(self) -> None:
        """Detener interfaz de bandeja"""
        if self.tray_icon:
            logger.info("⏹️ Deteniendo interfaz de bandeja...")
            self.tray_icon.stop()
