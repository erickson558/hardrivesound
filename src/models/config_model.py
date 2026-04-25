"""
Modelo de configuración para el simulador de disco duro.
Define la estructura y valores por defecto de la configuración.
"""
from dataclasses import dataclass, field
from typing import Dict
from src import __version__


@dataclass
class SoundConfig:
    """Configuración de un sonido individual"""
    enabled: bool = True
    file: str = ""
    volume: int = 100
    available: bool = False


@dataclass
class SoundTriggers:
    """Configuración de triggers de sonido"""
    read: bool = False
    write: bool = False
    both: bool = True


@dataclass
class AppConfig:
    """Configuración principal de la aplicación"""
    version: str = __version__
    enabled: bool = True
    global_delay: float = 1.0
    language: str = 'es'
    hdd_fade_profile: str = 'balanced'
    # Duracion del fade coseno aplicado a los archivos WAV reales (ms).
    fade_in_ms: float = 20.0
    fade_out_ms: float = 40.0
    method: str = 'winsound'
    minimize_to_tray: bool = True
    icon_behavior: str = 'write_priority'
    sound_triggers: SoundTriggers = field(default_factory=SoundTriggers)
    sounds: Dict[str, SoundConfig] = field(default_factory=dict)
    
    def __post_init__(self):
        """Inicializar configuración de sonidos por defecto"""
        self._normalize_language()
        self._normalize_fade_profile()
        self._normalize_sound_config()

    def _normalize_language(self) -> None:
        """Forzar idioma válido para evitar estados inválidos en UI."""
        if self.language not in {'es', 'en'}:
            self.language = 'es'

    def _normalize_fade_profile(self) -> None:
        """Forzar perfil de fade válido."""
        if self.hdd_fade_profile not in {'soft', 'balanced', 'aggressive'}:
            self.hdd_fade_profile = 'balanced'

    def _normalize_sound_config(self) -> None:
        """Completar claves faltantes para mantener compatibilidad con configs antiguas."""
        defaults = {
            'read': 'hdd_seek.wav',
            'write': 'hdd_seek.wav',
            'both': 'hdd_spin.wav'
        }

        if not self.sounds:
            self.sounds = {}

        for sound_type, file_name in defaults.items():
            if sound_type not in self.sounds:
                self.sounds[sound_type] = SoundConfig(enabled=True, file=file_name)
            elif not self.sounds[sound_type].file:
                self.sounds[sound_type].file = file_name
    
    def to_dict(self) -> dict:
        """Convertir configuración a diccionario"""
        return {
            'version': self.version,
            'enabled': self.enabled,
            'global_delay': self.global_delay,
            'language': self.language,
            'hdd_fade_profile': self.hdd_fade_profile,
            # Valores de fade guardados en JSON para persistencia entre sesiones
            'fade_in_ms': self.fade_in_ms,
            'fade_out_ms': self.fade_out_ms,
            'method': self.method,
            'minimize_to_tray': self.minimize_to_tray,
            'icon_behavior': self.icon_behavior,
            'sound_triggers': {
                'read': self.sound_triggers.read,
                'write': self.sound_triggers.write,
                'both': self.sound_triggers.both
            },
            'sounds': {
                sound_type: {
                    'enabled': config.enabled,
                    'file': config.file,
                    'volume': config.volume,
                    'available': config.available
                }
                for sound_type, config in self.sounds.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AppConfig':
        """Crear configuración desde diccionario"""
        sound_triggers = SoundTriggers(
            read=data.get('sound_triggers', {}).get('read', False),
            write=data.get('sound_triggers', {}).get('write', False),
            both=data.get('sound_triggers', {}).get('both', True)
        )
        
        sounds = {}
        for sound_type, sound_data in data.get('sounds', {}).items():
            sounds[sound_type] = SoundConfig(
                enabled=sound_data.get('enabled', True),
                file=sound_data.get('file', ''),
                volume=sound_data.get('volume', 100),
                available=sound_data.get('available', False)
            )
        
        return cls(
            version=data.get('version', __version__),
            fade_in_ms=data.get('fade_in_ms', 20.0),
            fade_out_ms=data.get('fade_out_ms', 40.0),
            enabled=data.get('enabled', True),
            global_delay=data.get('global_delay', 1.0),
            language=data.get('language', 'es'),
            hdd_fade_profile=data.get('hdd_fade_profile', 'balanced'),
            method=data.get('method', 'winsound'),
            minimize_to_tray=data.get('minimize_to_tray', True),
            icon_behavior=data.get('icon_behavior', 'write_priority'),
            sound_triggers=sound_triggers,
            sounds=sounds
        )
