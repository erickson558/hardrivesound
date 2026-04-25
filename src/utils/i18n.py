"""
Utilidades de internacionalización para la interfaz.
Centraliza textos ES/EN para evitar cadenas duplicadas en el frontend.
"""
from typing import Dict


TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "es": {
        "status.read": "Leyendo",
        "status.write": "Escribiendo",
        "status.both": "Leyendo/Escribiendo",
        "status.inactive": "Inactivo",
        "menu.no_config": "Sin configuracion",
        "menu.app_name": "{app_name}",
        "menu.version": "v{version}",
        "menu.mode": "{mode}",
        "menu.activities": "Actividades: {count}",
        "menu.global_section": "CONFIGURACION GLOBAL",
        "menu.global_sound": "Global: {state}",
        "menu.delay": "Delay: {delay}s",
        "menu.behavior": "Icono: {behavior}",
        "menu.style": "Estilo: {style}",
        "menu.language": "Idioma: {language}",
        "menu.trigger_section": "ACTIVAR SONIDO EN:",
        "menu.trigger.read": "Solo Lectura",
        "menu.trigger.write": "Solo Escritura",
        "menu.trigger.both": "Lectura+Escritura",
        "menu.sound_section": "SONIDOS INDIVIDUALES",
        "menu.sound.read": "Sonido Lectura",
        "menu.sound.write": "Sonido Escritura",
        "menu.sound.both": "Sonido Ambos",
        "menu.settings": "Abrir panel de configuracion",
        "menu.about": "Acerca de...",
        "menu.donate": "Comprame una cerveza",
        "menu.quit": "Salir",
        "gui.title": "Panel de configuracion",
        "gui.global_sound": "Activar sonido global",
        "gui.delay": "Delay entre sonidos",
        "gui.language": "Idioma",
        "gui.fade_profile": "Suavizado de audio",
        "gui.icon_behavior": "Comportamiento de icono",
        "gui.triggers": "Disparadores de actividad",
        "gui.sounds": "Sonidos habilitados",
        "gui.read": "Lectura",
        "gui.write": "Escritura",
        "gui.both": "Lectura + Escritura",
        "gui.apply": "Aplicar",
        "gui.close": "Cerrar",
        "gui.donate": "Comprame una cerveza",
        "gui.saved": "Configuracion aplicada correctamente",
        "gui.fade.soft": "Suave",
        "gui.fade.balanced": "Balanceado",
        "gui.fade.aggressive": "Agresivo",
            "gui.sound_files": "Archivos de sonido",
            "gui.sound_read_file": "Lectura",
            "gui.sound_write_file": "Escritura",
            "gui.fade_adjust": "Ajuste de Fade",
            "gui.fade_in": "Fade In (ms)",
            "gui.fade_out": "Fade Out (ms)",
        "about.title": "Acerca de",
        "about.version": "Version",
        "about.mode": "Modo",
        "about.style": "Estilo",
        "about.author": "Autor",
        "about.system": "Sistema",
        "about.uptime": "Tiempo activo",
        "about.activities": "Actividades",
        "mode.exe": "EXE",
        "mode.py": "PY",
        "state.on": "ON",
        "state.off": "OFF",
        "language.es": "Espanol",
        "language.en": "Ingles",
    },
    "en": {
        "status.read": "Reading",
        "status.write": "Writing",
        "status.both": "Reading/Writing",
        "status.inactive": "Idle",
        "menu.no_config": "No configuration",
        "menu.app_name": "{app_name}",
        "menu.version": "v{version}",
        "menu.mode": "{mode}",
        "menu.activities": "Activities: {count}",
        "menu.global_section": "GLOBAL SETTINGS",
        "menu.global_sound": "Global: {state}",
        "menu.delay": "Delay: {delay}s",
        "menu.behavior": "Icon: {behavior}",
        "menu.style": "Style: {style}",
        "menu.language": "Language: {language}",
        "menu.trigger_section": "PLAY SOUND ON:",
        "menu.trigger.read": "Read Only",
        "menu.trigger.write": "Write Only",
        "menu.trigger.both": "Read+Write",
        "menu.sound_section": "INDIVIDUAL SOUNDS",
        "menu.sound.read": "Read Sound",
        "menu.sound.write": "Write Sound",
        "menu.sound.both": "Both Sound",
        "menu.settings": "Open settings panel",
        "menu.about": "About...",
        "menu.donate": "Buy me a beer",
        "menu.quit": "Quit",
        "gui.title": "Settings panel",
        "gui.global_sound": "Enable global sound",
        "gui.delay": "Delay between sounds",
        "gui.language": "Language",
        "gui.fade_profile": "Audio smoothing",
        "gui.icon_behavior": "Icon behavior",
        "gui.triggers": "Activity triggers",
        "gui.sounds": "Enabled sounds",
        "gui.read": "Read",
        "gui.write": "Write",
        "gui.both": "Read + Write",
        "gui.apply": "Apply",
        "gui.close": "Close",
        "gui.donate": "Buy me a beer",
        "gui.saved": "Configuration applied successfully",
        "gui.fade.soft": "Soft",
        "gui.fade.balanced": "Balanced",
        "gui.fade.aggressive": "Aggressive",
            "gui.sound_files": "Sound files",
            "gui.sound_read_file": "Read",
            "gui.sound_write_file": "Write",
            "gui.fade_adjust": "Fade Adjustment",
            "gui.fade_in": "Fade In (ms)",
            "gui.fade_out": "Fade Out (ms)",
        "about.title": "About",
        "about.version": "Version",
        "about.mode": "Mode",
        "about.style": "Style",
        "about.author": "Author",
        "about.system": "System",
        "about.uptime": "Uptime",
        "about.activities": "Activities",
        "mode.exe": "EXE",
        "mode.py": "PY",
        "state.on": "ON",
        "state.off": "OFF",
        "language.es": "Spanish",
        "language.en": "English",
    },
}


class Translator:
    """Traductor simple con fallback a espanol."""

    def __init__(self, language: str = "es"):
        self.language = "es"
        self.set_language(language)

    def set_language(self, language: str) -> str:
        """Establece idioma activo y retorna el idioma aplicado."""
        self.language = language if language in TRANSLATIONS else "es"
        return self.language

    def t(self, key: str, **kwargs) -> str:
        """Obtiene texto traducido y aplica placeholders opcionales."""
        text = TRANSLATIONS.get(self.language, {}).get(key)
        if text is None:
            text = TRANSLATIONS["es"].get(key, key)

        if kwargs:
            return text.format(**kwargs)
        return text
