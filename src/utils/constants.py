"""
Constantes globales para el simulador de disco duro.
Define valores constantes utilizados en toda la aplicación.
"""
from src import __version__, __author__, __license__

# Información de la aplicación
APP_NAME = "Simulador Disco Duro Vintage"
APP_VERSION = __version__
APP_AUTHOR = __author__
APP_LICENSE = __license__
APP_DESCRIPTION = "Simula sonidos de disco duro antiguo con monitorización en tiempo real"
APP_YEAR = "2024"

# Configuración de sonido
DEFAULT_DELAY = 1.0
MIN_ACTIVITY_THRESHOLD = 5000  # bytes
ACTIVITY_TIMEOUT = 0.5  # segundos
MONITOR_INTERVAL = 0.1  # segundos

# Estilos de iconos disponibles
ICON_STYLES = ['modern', 'classic', 'simple', 'retro']

# Comportamientos de iconos disponibles
ICON_BEHAVIORS = ['write_priority', 'read_priority', 'both_green']

# Delays disponibles
AVAILABLE_DELAYS = [0.5, 1.0, 2.0, 3.0, 5.0]

# Idiomas disponibles
AVAILABLE_LANGUAGES = ['es', 'en']

# Donaciones
DONATION_URL = "https://www.paypal.com/donate/?hosted_button_id=ZABFRXC2P3JQN"

# Colores de iconos
ICON_COLOR_GREEN = "green"
ICON_COLOR_RED = "red"
ICON_COLOR_GRAY = "gray"

# Tipos de actividad
ACTIVITY_TYPE_READ = "read"
ACTIVITY_TYPE_WRITE = "write"
ACTIVITY_TYPE_BOTH = "both"
ACTIVITY_TYPE_INACTIVE = "inactive"

# Archivos
CONFIG_FILE = "config.json"
LOG_FILE = "hdd_simulator.log"

# Mensajes de estado
STATUS_READING = "Leyendo"
STATUS_WRITING = "Escribiendo"
STATUS_BOTH = "Leyendo/Escribiendo"
STATUS_INACTIVE = "Inactivo"
