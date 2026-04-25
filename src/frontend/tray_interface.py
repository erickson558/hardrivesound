"""
Interfaz de bandeja del sistema.
Maneja icono, menu y acciones de usuario.
"""
import time
import platform
import webbrowser
from typing import Optional, Callable
from src.utils.logger import logger
from src.utils.constants import (
    APP_NAME, APP_VERSION, APP_AUTHOR, APP_YEAR, APP_DESCRIPTION,
    ICON_STYLES, ACTIVITY_TYPE_READ, ACTIVITY_TYPE_WRITE,
    ACTIVITY_TYPE_BOTH, ACTIVITY_TYPE_INACTIVE, DONATION_URL
)
from src.utils.i18n import Translator
from src.frontend.icon_generator import IconGenerator

try:
    from pystray import Icon, Menu, MenuItem
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False
    logger.error("pystray no disponible")


class TrayInterface:
    """Interfaz de bandeja del sistema."""

    def __init__(self, is_compiled: bool = False, base_dir: str = ""):
        self.is_compiled = is_compiled
        self.base_dir = base_dir
        self.tray_icon: Optional[Icon] = None
        self.icon_style = 'modern'
        self.current_status = ACTIVITY_TYPE_INACTIVE
        self.activity_count = 0
        self.start_time = time.time()
        self.menu_update_pending = False

        # Traduccion activa del frontend.
        self.translator = Translator('es')

        # Callbacks
        self.on_toggle_global_sound: Optional[Callable] = None
        self.on_toggle_sound_type: Optional[Callable] = None
        self.on_toggle_sound_trigger: Optional[Callable] = None
        self.on_change_delay: Optional[Callable] = None
        self.on_change_icon_behavior: Optional[Callable] = None
        self.on_change_icon_style: Optional[Callable] = None
        self.on_change_language: Optional[Callable] = None
        self.on_open_settings: Optional[Callable] = None
        self.on_quit: Optional[Callable] = None

        self.config = None

        if not PYSTRAY_AVAILABLE:
            logger.error("TrayInterface no puede funcionar sin pystray")

    def set_config(self, config) -> None:
        """Establecer referencia a configuracion y sincronizar idioma."""
        self.config = config
        if self.config:
            self.set_language(self.config.language)

    def set_language(self, language: str) -> None:
        """Actualizar idioma de la interfaz y refrescar menu."""
        applied = self.translator.set_language(language)
        logger.info(f"Idioma de interfaz aplicado: {applied}")
        self.schedule_menu_update()
        self.process_pending_updates()

    def t(self, key: str, **kwargs) -> str:
        """Atajo de traduccion."""
        return self.translator.t(key, **kwargs)

    def create_icons(self) -> None:
        logger.info("Creando iconos de bandeja...")
        generator = IconGenerator(self.icon_style)

        self.idle_icon = generator.create_icon("gray")
        self.read_icon = generator.create_icon("green")
        self.write_icon = generator.create_icon("red")
        self.both_icon = generator.create_icon("green")

        logger.info("Iconos creados")

    def change_icon_style(self) -> str:
        current_index = ICON_STYLES.index(self.icon_style)
        new_index = (current_index + 1) % len(ICON_STYLES)
        self.icon_style = ICON_STYLES[new_index]

        self.create_icons()
        logger.info(f"Estilo cambiado a: {self.icon_style}")

        return self.icon_style

    def _status_label(self) -> str:
        return self.t(f"status.{self.current_status}")

    def update_icon_color(self, activity_type: str) -> None:
        try:
            if not self.tray_icon:
                return

            if activity_type == ACTIVITY_TYPE_READ:
                self.tray_icon.icon = self.read_icon
                self.current_status = ACTIVITY_TYPE_READ
            elif activity_type == ACTIVITY_TYPE_WRITE:
                self.tray_icon.icon = self.write_icon
                self.current_status = ACTIVITY_TYPE_WRITE
            elif activity_type == ACTIVITY_TYPE_BOTH:
                self.tray_icon.icon = self.both_icon
                self.current_status = ACTIVITY_TYPE_BOTH
            else:
                self.tray_icon.icon = self.idle_icon
                self.current_status = ACTIVITY_TYPE_INACTIVE

            self.schedule_menu_update()
            logger.debug(f"Icono actualizado: {self.current_status}")
        except Exception as e:
            logger.error(f"Error actualizando icono: {e}")

    def schedule_menu_update(self) -> None:
        self.menu_update_pending = True

    def process_pending_updates(self) -> None:
        if self.menu_update_pending:
            self.menu_update_pending = False
            self.update_menu()

    def increment_activity_count(self) -> None:
        self.activity_count += 1

    def get_uptime(self) -> str:
        uptime = time.time() - self.start_time
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def show_about_info(self) -> None:
        """Registrar info de diagnostico sin abrir ventanas extra."""
        mode_text = self.t('mode.exe') if self.is_compiled else self.t('mode.py')
        lines = [
            f"{self.t('about.title')}: {APP_NAME}",
            f"{self.t('about.version')}: {APP_VERSION}",
            f"{self.t('about.mode')}: {mode_text}",
            f"{self.t('about.style')}: {self.icon_style.title()}",
            f"{self.t('about.author')}: {APP_AUTHOR} ({APP_YEAR})",
            f"{self.t('about.system')}: Python {platform.python_version()} - {platform.system()} {platform.release()}",
            f"{self.t('about.uptime')}: {self.get_uptime()}",
            f"{self.t('about.activities')}: {self.activity_count}",
            APP_DESCRIPTION,
        ]
        logger.info("\n".join(lines))

    def open_donation_link(self) -> None:
        """Abrir enlace de donacion en navegador por defecto."""
        try:
            webbrowser.open(DONATION_URL, new=2)
            logger.info("Enlace de donacion abierto en navegador")
        except Exception as e:
            logger.error(f"No se pudo abrir enlace de donacion: {e}")

    def create_menu_action(self, action_function: Callable, *args) -> Callable:
        def menu_action(icon, item):
            try:
                action_function(*args)
                self.schedule_menu_update()
            except Exception as e:
                logger.error(f"Error en accion de menu: {e}")
        return menu_action

    def build_menu(self) -> Menu:
        if not self.config:
            return Menu(
                MenuItem(f"⚠️ {self.t('menu.no_config')}", None, enabled=False),
                MenuItem(f"❌ {self.t('menu.quit')}", lambda i, _: self.on_quit() if self.on_quit else None)
            )

        global_state = self.t('state.on') if self.config.enabled else self.t('state.off')
        language_name = self.t(f"language.{self.config.language}")
        mode_text = self.t('mode.exe') if self.is_compiled else self.t('mode.py')

        global_sound_text = f"🔊 {self.t('menu.global_sound', state=global_state)}"
        delay_text = f"⏱️ {self.t('menu.delay', delay=self.config.global_delay)}"
        behavior_text = f"🎨 {self.t('menu.behavior', behavior=self.config.icon_behavior.replace('_', ' ').title())}"
        style_text = f"🖼️ {self.t('menu.style', style=self.icon_style.title())}"
        language_text = f"🌐 {self.t('menu.language', language=language_name)}"

        read_status = "✅" if self.config.sounds['read'].enabled else "❌"
        write_status = "✅" if self.config.sounds['write'].enabled else "❌"
        both_status = "✅" if self.config.sounds['both'].enabled else "❌"

        read_trigger = "🔊" if self.config.sound_triggers.read else "🔇"
        write_trigger = "🔊" if self.config.sound_triggers.write else "🔇"
        both_trigger = "🔊" if self.config.sound_triggers.both else "🔇"

        status_icons = {
            ACTIVITY_TYPE_READ: "🟢",
            ACTIVITY_TYPE_WRITE: "🔴",
            ACTIVITY_TYPE_BOTH: "🟡",
            ACTIVITY_TYPE_INACTIVE: "⚫"
        }
        status_icon = status_icons.get(self.current_status, "⚫")

        return Menu(
            MenuItem(f"💾 {self.t('menu.app_name', app_name=APP_NAME)}", None, enabled=False),
            MenuItem(f"📦 {self.t('menu.version', version=APP_VERSION)}", None, enabled=False),
            MenuItem(f"🔧 {self.t('menu.mode', mode=mode_text)}", None, enabled=False),
            MenuItem(f"{status_icon} {self._status_label()}", None, enabled=False),
            MenuItem(f"🎯 {self.t('menu.activities', count=self.activity_count)}", None, enabled=False),
            MenuItem('---', None, enabled=False),

            MenuItem(f"🎛️ {self.t('menu.global_section')}", None, enabled=False),
            MenuItem(global_sound_text, self.create_menu_action(self._handle_toggle_global)),
            MenuItem(delay_text, self.create_menu_action(self._handle_change_delay)),
            MenuItem(behavior_text, self.create_menu_action(self._handle_change_behavior)),
            MenuItem(style_text, self.create_menu_action(self._handle_change_style)),
            MenuItem(language_text, self.create_menu_action(self._handle_change_language)),
            MenuItem('---', None, enabled=False),

            MenuItem(f"🔊 {self.t('menu.trigger_section')}", None, enabled=False),
            MenuItem(f"{read_trigger} {self.t('menu.trigger.read')}", self.create_menu_action(self._handle_toggle_trigger, 'read')),
            MenuItem(f"{write_trigger} {self.t('menu.trigger.write')}", self.create_menu_action(self._handle_toggle_trigger, 'write')),
            MenuItem(f"{both_trigger} {self.t('menu.trigger.both')}", self.create_menu_action(self._handle_toggle_trigger, 'both')),
            MenuItem('---', None, enabled=False),

            MenuItem(f"📖 {self.t('menu.sound_section')}", None, enabled=False),
            MenuItem(f"{read_status} {self.t('menu.sound.read')}", self.create_menu_action(self._handle_toggle_sound, 'read')),
            MenuItem(f"{write_status} {self.t('menu.sound.write')}", self.create_menu_action(self._handle_toggle_sound, 'write')),
            MenuItem(f"{both_status} {self.t('menu.sound.both')}", self.create_menu_action(self._handle_toggle_sound, 'both')),
            MenuItem('---', None, enabled=False),

            # En Windows, el item por defecto se activa con doble click en el icono de tray.
            MenuItem(
                f"⚙️ {self.t('menu.settings')}",
                self.create_menu_action(self._handle_open_settings),
                default=True,
            ),
            MenuItem(f"🍺 {self.t('menu.donate')}", lambda i, _: self.open_donation_link()),
            MenuItem(f"ℹ️ {self.t('menu.about')}", lambda i, _: self.show_about_info()),
            MenuItem('---', None, enabled=False),
            MenuItem(f"❌ {self.t('menu.quit')}", lambda i, _: self.on_quit() if self.on_quit else None)
        )

    def _handle_toggle_global(self) -> None:
        if self.on_toggle_global_sound:
            self.on_toggle_global_sound()

    def _handle_toggle_sound(self, sound_type: str) -> None:
        if self.on_toggle_sound_type:
            self.on_toggle_sound_type(sound_type)

    def _handle_toggle_trigger(self, trigger_type: str) -> None:
        if self.on_toggle_sound_trigger:
            self.on_toggle_sound_trigger(trigger_type)

    def _handle_change_delay(self) -> None:
        if self.on_change_delay:
            self.on_change_delay()

    def _handle_change_behavior(self) -> None:
        if self.on_change_icon_behavior:
            self.on_change_icon_behavior()

    def _handle_change_style(self) -> None:
        new_style = self.change_icon_style()
        if self.on_change_icon_style:
            self.on_change_icon_style(new_style)

    def _handle_change_language(self) -> None:
        if self.on_change_language:
            self.on_change_language()

    def _handle_open_settings(self) -> None:
        if self.on_open_settings:
            self.on_open_settings()

    def initialize(self) -> None:
        if not PYSTRAY_AVAILABLE:
            logger.error("No se puede inicializar - pystray no disponible")
            return

        logger.info("Inicializando interfaz de bandeja...")
        self.create_icons()

        menu = self.build_menu()
        self.tray_icon = Icon('hard_drive_simulator')
        self.tray_icon.title = f"{APP_NAME} v{APP_VERSION} - {self._status_label()}"
        self.tray_icon.menu = menu
        self.tray_icon.icon = self.idle_icon

        logger.info("Interfaz de bandeja inicializada")

    def update_menu(self) -> None:
        if self.tray_icon:
            self.tray_icon.menu = self.build_menu()
            self.tray_icon.title = f"{APP_NAME} v{APP_VERSION} - {self._status_label()}"
            logger.debug("Menu actualizado")

    def run(self) -> None:
        if self.tray_icon:
            logger.info("Iniciando bucle de interfaz de bandeja...")
            self.tray_icon.run()

    def stop(self) -> None:
        if self.tray_icon:
            logger.info("Deteniendo interfaz de bandeja...")
            self.tray_icon.stop()
