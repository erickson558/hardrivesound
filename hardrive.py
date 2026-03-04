import time
import threading
import os
import sys
import signal
import json
import winsound
import platform
from datetime import datetime
import logging
import traceback

# Configurar logging ANTES de cualquier otra importación
def setup_logging():
    """Configurar sistema de logging robusto"""
    try:
        # Determinar directorio base
        is_compiled = getattr(sys, 'frozen', False)
        if is_compiled:
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        log_file = os.path.join(base_dir, 'hdd_simulator.log')
        
        # Configurar logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()  # También mostrar en consola
            ]
        )
        
        logging.info("=" * 60)
        logging.info("INICIANDO SIMULADOR DE DISCO DURO VINTAGE")
        logging.info("=" * 60)
        logging.info(f"Directorio base: {base_dir}")
        logging.info(f"Archivo log: {log_file}")
        logging.info(f"Python: {platform.python_version()}")
        logging.info(f"Sistema: {platform.system()} {platform.release()}")
        logging.info(f"Compilado: {is_compiled}")
        
        return True
    except Exception as e:
        print(f"ERROR CRÍTICO configurando log: {e}")
        return False

# Ejecutar configuración de logging inmediatamente
setup_logging()

try:
    import psutil
    PSUTIL_AVAILABLE = True
    logging.info("✅ psutil importado correctamente")
except ImportError as e:
    PSUTIL_AVAILABLE = False
    logging.error(f"❌ Error importando psutil: {e}")

try:
    from pystray import Icon, Menu, MenuItem
    from PIL import Image, ImageDraw
    PILLOW_AVAILABLE = True
    logging.info("✅ pystray y PIL importados correctamente")
except ImportError as e:
    PILLOW_AVAILABLE = False
    logging.error(f"❌ Error importando pystray/PIL: {e}")

class HardDriveSimulator:
    def __init__(self):
        try:
            logging.info("Inicializando HardDriveSimulator...")
            
            self.is_running = True
            self.tray_icon = None
            self.activity_count = 0
            
            # Detectar si estamos ejecutando como .exe o .py
            self.is_compiled = getattr(sys, 'frozen', False)
            logging.info(f"Modo ejecución: {'Compilado (.exe)' if self.is_compiled else 'Script (.py)'}")
            
            # Obtener la ruta correcta para config.json
            if self.is_compiled:
                self.base_dir = os.path.dirname(sys.executable)
            else:
                self.base_dir = os.path.dirname(os.path.abspath(__file__))
            
            self.config_file = os.path.join(self.base_dir, 'config.json')
            logging.info(f"Directorio base: {self.base_dir}")
            logging.info(f"Archivo config: {self.config_file}")
            
            # Información de versión
            self.app_info = {
                'name': 'Simulador Disco Duro Vintage',
                'version': '2.1.1',
                'author': 'Erickson',
                'description': 'Simula sonidos de disco duro antiguo con monitorización en tiempo real',
                'year': '2024'
            }
            
            # Estilo del icono
            self.icon_style = 'modern'
            
            # Control de menú
            self.menu_update_pending = False
            
            # Cargar configuración
            self.sound_config = self.load_config()
            
            # Control
            self.sound_cooldown_until = 0
            self.current_status = "Inactivo"
            self.last_activity_type = None
            self.activity_timeout = 0
            
            # Verificar dependencias
            if not PSUTIL_AVAILABLE:
                logging.error("❌ psutil no disponible - la aplicación no funcionará correctamente")
                return
                
            if not PILLOW_AVAILABLE:
                logging.error("❌ pystray/PIL no disponibles - no se puede crear icono en bandeja")
                return
            
            logging.info("Creando icono en bandeja del sistema...")
            self.create_tray_icon()
            
            logging.info("Ocultando consola...")
            self.hide_console()
            
            # Mostrar información de inicio
            self.show_startup_info()
            
            logging.info("✅ HardDriveSimulator inicializado correctamente")
            
        except Exception as e:
            logging.error(f"❌ ERROR CRÍTICO en __init__: {e}")
            logging.error(traceback.format_exc())
            raise
    
    def show_startup_info(self):
        """Mostrar información de inicio en consola (oculta)"""
        try:
            info = f"""
╔══════════════════════════════════════════════════╗
║             {self.app_info['name']}             ║
╠══════════════════════════════════════════════════╣
║  Versión: {self.app_info['version']}                            ║
║  Modo: {'Compilado (.exe)' if self.is_compiled else 'Script (.py)'}                  ║
║  Carpeta: {os.path.basename(self.base_dir)}                    ║
║  Config: {os.path.basename(self.config_file)}                    ║
║  Estilo: {self.icon_style.title()}                            ║
║                                                    ║
║  • Monitorización en tiempo real activada         ║
║  • Sonidos vintage configurados                   ║
║  • Icono en bandeja del sistema listo             ║
║  • Menú persistente activado                      ║
║                                                    ║
║  Click derecho en el ícono para configuración     ║
║  Click fuera del menú para cerrarlo               ║
╚══════════════════════════════════════════════════╝
"""
            logging.info(info)
        except Exception as e:
            logging.error(f"Error en show_startup_info: {e}")
    
    def hide_console(self):
        """Ocultar la ventana de consola"""
        try:
            import ctypes
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
            logging.info("✅ Consola ocultada")
        except Exception as e:
            logging.warning(f"⚠️ No se pudo ocultar la consola: {e}")
    
    def get_resource_path(self, filename):
        """Obtener la ruta correcta para archivos de recursos"""
        path = os.path.join(self.base_dir, filename)
        logging.debug(f"Buscando recurso: {filename} -> {path}")
        return path
    
    def load_config(self):
        """Cargar configuración desde archivo"""
        logging.info("Cargando configuración...")
        
        default_config = {
            'version': self.app_info['version'],
            'enabled': True,
            'global_delay': 1.0,
            'method': 'winsound',
            'minimize_to_tray': True,
            'icon_behavior': 'write_priority',
            'sound_triggers': {
                'read': True,
                'write': True, 
                'both': True
            },
            'sounds': {
                'read': {
                    'enabled': True,
                    'file': 'hdd_seek.wav',
                    'volume': 100
                },
                'write': {
                    'enabled': True,
                    'file': 'hdd_click.wav',
                    'volume': 100
                },
                'both': {
                    'enabled': True,
                    'file': 'hdd_spin.wav',
                    'volume': 100
                }
            }
        }
        
        logging.info(f"Buscando configuración en: {self.config_file}")
        
        try:
            if os.path.exists(self.config_file):
                logging.info("✅ Archivo config.json encontrado")
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    
                    if 'version' in loaded_config:
                        self.app_info['config_version'] = loaded_config['version']
                        logging.info(f"Versión de configuración: {loaded_config['version']}")
                    
                    config = self.merge_configs(default_config, loaded_config)
                    logging.info("✅ Configuración cargada exitosamente")
                    return config
            else:
                logging.warning("⚠️ Archivo config.json no encontrado, usando configuración por defecto")
                self.create_default_config(default_config)
                
        except Exception as e:
            logging.error(f"❌ Error cargando configuración: {e}")
            logging.error(traceback.format_exc())
            logging.info("⚠️ Usando configuración por defecto")
        
        return default_config
    
    def create_default_config(self, config):
        """Crear archivo de configuración por defecto si no existe"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            logging.info(f"✅ Archivo config.json creado en: {self.config_file}")
        except Exception as e:
            logging.error(f"❌ Error creando config.json: {e}")
    
    def merge_configs(self, default, loaded):
        """Combinar configuraciones"""
        result = default.copy()
        
        for key in ['enabled', 'global_delay', 'method', 'minimize_to_tray', 'icon_behavior']:
            if key in loaded:
                result[key] = loaded[key]
        
        if 'sound_triggers' in loaded:
            for trigger in ['read', 'write', 'both']:
                if trigger in loaded['sound_triggers']:
                    result['sound_triggers'][trigger] = loaded['sound_triggers'][trigger]
        
        if 'sounds' in loaded:
            for sound_type in ['read', 'write', 'both']:
                if sound_type in loaded['sounds']:
                    for key in ['enabled', 'file', 'volume']:
                        if key in loaded['sounds'][sound_type]:
                            result['sounds'][sound_type][key] = loaded['sounds'][sound_type][key]
        
        return result
    
    def save_config(self):
        """Guardar configuración en archivo"""
        try:
            self.sound_config['version'] = self.app_info['version']
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.sound_config, f, indent=4, ensure_ascii=False)
            
            logging.info(f"✅ Configuración guardada en: {self.config_file}")
        except Exception as e:
            logging.error(f"❌ Error guardando configuración: {e}")
    
    def check_sound_files(self):
        """Verificar archivos de sonido"""
        logging.info("Verificando archivos de sonido...")
        
        for sound_type in ['read', 'write', 'both']:
            config = self.sound_config['sounds'][sound_type]
            sound_file_path = self.get_resource_path(config['file'])
            config['available'] = os.path.exists(sound_file_path)
            
            if config['available']:
                logging.info(f"   ✅ {config['file']} - ENCONTRADO")
            else:
                logging.error(f"   ❌ {config['file']} - NO ENCONTRADO en: {sound_file_path}")
    
    def play_sound_winsound_silent(self, filename):
        """Reproducir sonido SILENCIOSO"""
        sound_file_path = self.get_resource_path(filename)
        
        try:
            if os.path.exists(sound_file_path):
                winsound.PlaySound(sound_file_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                logging.debug(f"🔊 Sonido reproducido: {filename}")
                return True
            else:
                logging.error(f"❌ Archivo de sonido no encontrado: {sound_file_path}")
        except Exception as e:
            logging.error(f"❌ Error reproduciendo sonido: {e}")
        return False
    
    def play_sound_by_type(self, sound_type):
        """Reproducir sonido según actividad"""
        if not self.sound_config['enabled']:
            return False
        
        if not self.sound_config['sound_triggers'].get(sound_type, True):
            return False
            
        config = self.sound_config['sounds'].get(sound_type)
        if not config or not config['enabled'] or not config.get('available', False):
            return False
            
        if time.time() < self.sound_cooldown_until:
            return False
        
        filename = config['file']
        success = False
        
        if self.sound_config['method'] == 'winsound':
            success = self.play_sound_winsound_silent(filename)
        
        if success:
            self.sound_cooldown_until = time.time() + self.sound_config['global_delay']
            logging.debug(f"✅ Sonido {sound_type} reproducido exitosamente")
            return True
        
        return False
    
    def determine_icon_color(self, read_active, write_active):
        """Determinar color del icono"""
        behavior = self.sound_config.get('icon_behavior', 'write_priority')
        
        if read_active and write_active:
            if behavior == 'both_green':
                return "green", "both"
            elif behavior == 'read_priority':
                return "green", "read"
            else:
                return "red", "write"
        elif write_active:
            return "red", "write"
        elif read_active:
            return "green", "read"
        else:
            return "gray", "inactive"
    
    def update_icon_color(self, activity_type):
        """Actualizar color del icono"""
        try:
            if activity_type == "read":
                self.tray_icon.icon = self.read_icon
                self.current_status = "Leyendo"
            elif activity_type == "write":
                self.tray_icon.icon = self.write_icon
                self.current_status = "Escribiendo"
            elif activity_type == "both":
                self.tray_icon.icon = self.both_icon
                self.current_status = "Leyendo/Escribiendo"
            else:
                self.tray_icon.icon = self.idle_icon
                self.current_status = "Inactivo"
            
            self.schedule_menu_update()
            logging.debug(f"Ícono actualizado: {self.current_status}")
        except Exception as e:
            logging.error(f"Error actualizando icono: {e}")
    
    def schedule_menu_update(self):
        """Programar actualización del menú (no inmediata)"""
        self.menu_update_pending = True
    
    def process_pending_updates(self):
        """Procesar actualizaciones pendientes del menú"""
        if self.menu_update_pending:
            self.menu_update_pending = False
            self.update_tray_menu()
    
    # =============================================
    # MÉTODOS DE CONFIGURACIÓN MEJORADOS
    # =============================================
    
    def create_menu_action(self, action_function, *args):
        """Crear una acción de menú que no cierre el menú inmediatamente"""
        def menu_action(icon, item):
            try:
                action_function(*args)
                # No actualizamos el menú inmediatamente para que no se cierre
                self.schedule_menu_update()
            except Exception as e:
                logging.error(f"Error en acción de menú: {e}")
        return menu_action
    
    def toggle_global_sound(self):
        """Activar/desactivar sonido global"""
        self.sound_config['enabled'] = not self.sound_config['enabled']
        self.save_config()
        status = 'ACTIVADO' if self.sound_config['enabled'] else 'DESACTIVADO'
        logging.info(f"🔊 Sonido global: {status}")
    
    def toggle_sound_type(self, sound_type):
        """Activar/desactivar sonido específico"""
        def toggle():
            self.sound_config['sounds'][sound_type]['enabled'] = not self.sound_config['sounds'][sound_type]['enabled']
            self.save_config()
            status = "activado" if self.sound_config['sounds'][sound_type]['enabled'] else "desactivado"
            logging.info(f"🔊 Sonido {sound_type} {status}")
        return toggle
    
    def toggle_sound_trigger(self, trigger_type):
        """Activar/desactivar trigger de sonido"""
        def toggle():
            self.sound_config['sound_triggers'][trigger_type] = not self.sound_config['sound_triggers'][trigger_type]
            self.save_config()
            status = "activado" if self.sound_config['sound_triggers'][trigger_type] else "desactivado"
            logging.info(f"🔊 Trigger {trigger_type} {status}")
        return toggle
    
    def change_global_delay(self):
        """Cambiar delay global"""
        current = self.sound_config['global_delay']
        delays = [0.5, 1.0, 2.0, 3.0, 5.0]
        current_index = delays.index(current) if current in delays else 1
        new_index = (current_index + 1) % len(delays)
        self.sound_config['global_delay'] = delays[new_index]
        self.save_config()
        logging.info(f"⏱️ Nuevo delay: {self.sound_config['global_delay']}s")
    
    def change_icon_behavior(self):
        """Cambiar comportamiento del icono"""
        behaviors = ['write_priority', 'read_priority', 'both_green']
        current = self.sound_config.get('icon_behavior', 'write_priority')
        current_index = behaviors.index(current) if current in behaviors else 0
        new_index = (current_index + 1) % len(behaviors)
        self.sound_config['icon_behavior'] = behaviors[new_index]
        self.save_config()
        logging.info(f"🎨 Comportamiento del icono: {self.sound_config['icon_behavior']}")
    
    def change_icon_style(self):
        """Cambiar estilo del icono"""
        styles = ['modern', 'classic', 'simple', 'retro']
        current_index = styles.index(self.icon_style)
        new_index = (current_index + 1) % len(styles)
        self.icon_style = styles[new_index]
        
        # Recrear los iconos con el nuevo estilo
        self.create_tray_icon()
        logging.info(f"🎨 Cambiando a estilo: {self.icon_style.title()}")
    
    def show_about_info(self):
        """Mostrar información 'Acerca de'"""
        about_text = f"""
{self.app_info['name']}

Versión: {self.app_info['version']}
Modo: {'Compilado (.exe)' if self.is_compiled else 'Script (.py)'}
Estilo: {self.icon_style.title()}
Configuración: v{self.sound_config.get('version', 'N/A')}

Autor: {self.app_info['author']}
Año: {self.app_info['year']}

Ubicación:
• Ejecutable: {self.base_dir}
• Configuración: {self.config_file}

Descripción:
{self.app_info['description']}

Características:
• Monitorización en tiempo real de disco
• Sonidos vintage personalizables  
• 4 estilos de icono diferentes
• Configuración persistente
• Menú que permanece abierto
• Compatible con .py y .exe

Sistema:
• Python {platform.python_version()}
• {platform.system()} {platform.release()}
• Tiempo activo: {self.get_uptime()}
• Actividades detectadas: {self.activity_count}
"""
        logging.info(f"Información 'Acerca de':\n{about_text}")
    
    def get_uptime(self):
        """Obtener tiempo de actividad"""
        if hasattr(self, 'start_time'):
            uptime = time.time() - self.start_time
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            seconds = int(uptime % 60)
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return "00:00:00"
    
    def create_modern_icon(self, color):
        """Icono moderno"""
        try:
            width, height = 64, 64
            image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            dc = ImageDraw.Draw(image)
            
            if color == "green": 
                fill_color = (76, 175, 80, 255)
                accent_color = (56, 142, 60, 255)
            elif color == "red": 
                fill_color = (244, 67, 54, 255)
                accent_color = (198, 40, 40, 255)
            else: 
                fill_color = (158, 158, 158, 255)
                accent_color = (97, 97, 97, 255)
            
            dc.ellipse([6, 6, width-6, height-6], fill=fill_color, outline=accent_color, width=2)
            dc.ellipse([10, 10, 22, 22], fill=(255, 255, 255, 60))
            dc.ellipse([30, 30, 34, 34], fill=(255, 255, 255, 200))
            
            for i in range(4):
                angle = i * 90
                start_angle = angle - 20
                end_angle = angle + 20
                dc.arc([15, 15, width-15, height-15], start_angle, end_angle, 
                      fill=(255, 255, 255, 120), width=3)
            
            return image
        except Exception as e:
            logging.error(f"Error creando icono moderno: {e}")
            # Icono de fallback
            image = Image.new('RGB', (64, 64), 'red')
            return image
    
    def create_classic_icon(self, color):
        """Icono clásico"""
        try:
            width, height = 64, 64
            image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            dc = ImageDraw.Draw(image)
            
            if color == "green": 
                fill_color = (0, 150, 0, 255)
                plate_color = (0, 100, 0, 255)
            elif color == "red": 
                fill_color = (200, 0, 0, 255)
                plate_color = (150, 0, 0, 255)
            else: 
                fill_color = (100, 100, 100, 255)
                plate_color = (70, 70, 70, 255)
            
            dc.ellipse([4, 4, width-4, height-4], fill=fill_color, outline=(0, 0, 0, 255), width=3)
            
            for i in range(3):
                size = 20 + i * 12
                pos = (width - size) // 2
                dc.ellipse([pos, pos, pos+size, pos+size], fill=plate_color, outline=(0, 0, 0, 255), width=1)
            
            dc.rectangle([30, 15, 33, 35], fill=(200, 200, 200, 255))
            dc.ellipse([28, 35, 35, 42], fill=(150, 150, 150, 255))
            dc.rectangle([25, 12, 38, 15], fill=(50, 50, 50, 255))
            
            return image
        except Exception as e:
            logging.error(f"Error creando icono clásico: {e}")
            image = Image.new('RGB', (64, 64), 'blue')
            return image
    
    def create_simple_icon(self, color):
        """Icono simple"""
        try:
            width, height = 64, 64
            image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            dc = ImageDraw.Draw(image)
            
            if color == "green": 
                fill_color = (0, 200, 0, 255)
            elif color == "red": 
                fill_color = (255, 0, 0, 255)
            else: 
                fill_color = (150, 150, 150, 255)
            
            dc.ellipse([8, 8, width-8, height-8], fill=fill_color)
            dc.ellipse([30, 30, 34, 34], fill=(255, 255, 255, 200))
            
            return image
        except Exception as e:
            logging.error(f"Error creando icono simple: {e}")
            image = Image.new('RGB', (64, 64), 'green')
            return image
    
    def create_retro_icon(self, color):
        """Icono retro"""
        try:
            width, height = 64, 64
            image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            dc = ImageDraw.Draw(image)
            
            if color == "green": 
                fill_color = (0, 255, 0, 255)
                glow_color = (0, 200, 0, 100)
            elif color == "red": 
                fill_color = (255, 0, 0, 255)
                glow_color = (200, 0, 0, 100)
            else: 
                fill_color = (128, 128, 128, 255)
                glow_color = (100, 100, 100, 100)
            
            dc.ellipse([2, 2, width-2, height-2], fill=glow_color)
            dc.ellipse([6, 6, width-6, height-6], fill=fill_color, outline=(0, 0, 0, 255), width=2)
            
            for i in range(8):
                x1 = 10 + i * 6
                y1 = 10
                x2 = 10
                y2 = 10 + i * 6
                dc.line([x1, y1, x2, y2], fill=(255, 255, 255, 80), width=1)
            
            dc.text((20, 25), "HDD", fill=(0, 0, 0, 200))
            
            return image
        except Exception as e:
            logging.error(f"Error creando icono retro: {e}")
            image = Image.new('RGB', (64, 64), 'yellow')
            return image
    
    def create_icon_image(self, color):
        """Crear icono según el estilo seleccionado"""
        try:
            if self.icon_style == 'modern':
                return self.create_modern_icon(color)
            elif self.icon_style == 'classic':
                return self.create_classic_icon(color)
            elif self.icon_style == 'simple':
                return self.create_simple_icon(color)
            elif self.icon_style == 'retro':
                return self.create_retro_icon(color)
            else:
                return self.create_modern_icon(color)
        except Exception as e:
            logging.error(f"Error en create_icon_image: {e}")
            # Icono de fallback
            image = Image.new('RGB', (64, 64), 'gray')
            return image
    
    def create_tray_icon(self):
        """Crear icono del sistema"""
        try:
            logging.info("Creando iconos del sistema...")
            self.start_time = time.time()
            
            self.idle_icon = self.create_icon_image("gray")
            self.read_icon = self.create_icon_image("green")
            self.write_icon = self.create_icon_image("red")
            self.both_icon = self.create_icon_image("green")
            
            self.check_sound_files()
            self.update_tray_menu()
            logging.info("✅ Iconos del sistema creados correctamente")
        except Exception as e:
            logging.error(f"❌ Error creando icono del sistema: {e}")
            logging.error(traceback.format_exc())
            raise
    
    def update_tray_menu(self):
        """Actualizar menú del tray"""
        try:
            if not self.tray_icon:
                menu = self._build_menu()
                self.tray_icon = Icon('hard_drive_simulator')
                self.tray_icon.title = f"{self.app_info['name']} v{self.app_info['version']} - {self.current_status}"
                self.tray_icon.menu = menu
                self.tray_icon.icon = self.idle_icon
                logging.info("✅ Tray icon creado por primera vez")
            else:
                self.tray_icon.menu = self._build_menu()
                self.tray_icon.title = f"{self.app_info['name']} v{self.app_info['version']} - {self.current_status}"
                logging.debug("✅ Menú del tray actualizado")
        except Exception as e:
            logging.error(f"❌ Error actualizando menú del tray: {e}")
    
    def _build_menu(self):
        """Construir menú completo con acciones mejoradas"""
        try:
            global_sound_text = f'🔊 Global: {"ON" if self.sound_config["enabled"] else "OFF"}'
            delay_text = f'⏱️ Delay: {self.sound_config["global_delay"]}s'
            
            behavior = self.sound_config.get('icon_behavior', 'write_priority')
            behavior_text = f'🎨 Comportamiento: {behavior.replace("_", " ").title()}'
            
            style_text = f'🖼️ Estilo Icono: {self.icon_style.title()}'
            
            read_status = "✅" if self.sound_config['sounds']['read']['enabled'] else "❌"
            write_status = "✅" if self.sound_config['sounds']['write']['enabled'] else "❌"
            both_status = "✅" if self.sound_config['sounds']['both']['enabled'] else "❌"
            
            read_trigger = "🔊" if self.sound_config['sound_triggers']['read'] else "🔇"
            write_trigger = "🔊" if self.sound_config['sound_triggers']['write'] else "🔇"
            both_trigger = "🔊" if self.sound_config['sound_triggers']['both'] else "🔇"
            
            status_icon = "🟢" if self.current_status == "Leyendo" else "🔴" if self.current_status == "Escribiendo" else "🟡" if self.current_status == "Leyendo/Escribiendo" else "⚫"
            
            return Menu(
                MenuItem(f'💾 {self.app_info["name"]}', None, enabled=False),
                MenuItem(f'📦 v{self.app_info["version"]}', None, enabled=False),
                MenuItem(f'🔧 {"EXE" if self.is_compiled else "PY"}', None, enabled=False),
                MenuItem(f'{status_icon} {self.current_status}', None, enabled=False),
                MenuItem(f'🎯 Actividades: {self.activity_count}', None, enabled=False),
                MenuItem('---', None, enabled=False),
                
                MenuItem('🎛️ CONFIGURACIÓN GLOBAL', None, enabled=False),
                MenuItem(global_sound_text, self.create_menu_action(self.toggle_global_sound)),
                MenuItem(delay_text, self.create_menu_action(self.change_global_delay)),
                MenuItem(behavior_text, self.create_menu_action(self.change_icon_behavior)),
                MenuItem(style_text, self.create_menu_action(self.change_icon_style)),
                MenuItem('---', None, enabled=False),
                
                MenuItem('🔊 ACTIVAR SONIDO EN:', None, enabled=False),
                MenuItem(f'{read_trigger} Solo Lectura', self.create_menu_action(self.toggle_sound_trigger('read'))),
                MenuItem(f'{write_trigger} Solo Escritura', self.create_menu_action(self.toggle_sound_trigger('write'))),
                MenuItem(f'{both_trigger} Lectura+Escritura', self.create_menu_action(self.toggle_sound_trigger('both'))),
                MenuItem('---', None, enabled=False),
                
                MenuItem('📖 SONIDOS INDIVIDUALES', None, enabled=False),
                MenuItem(f'{read_status} Sonido Lectura', self.create_menu_action(self.toggle_sound_type('read'))),
                MenuItem(f'{write_status} Sonido Escritura', self.create_menu_action(self.toggle_sound_type('write'))),
                MenuItem(f'{both_status} Sonido Ambos', self.create_menu_action(self.toggle_sound_type('both'))),
                MenuItem('---', None, enabled=False),
                
                MenuItem('ℹ️ Acerca de...', lambda icon, item: self.show_about_info()),
                MenuItem('---', None, enabled=False),
                MenuItem('❌ Salir', self.quit_program)
            )
        except Exception as e:
            logging.error(f"❌ Error construyendo menú: {e}")
            # Menú de emergencia
            return Menu(
                MenuItem('❌ ERROR - Ver log', None, enabled=False),
                MenuItem('❌ Salir', self.quit_program)
            )
    
    def monitor_disk_activity(self):
        """Monitorear actividad del disco"""
        if not PSUTIL_AVAILABLE:
            logging.error("No se puede monitorear actividad - psutil no disponible")
            return
            
        logging.info("Iniciando monitoreo de actividad del disco...")
        previous_stats = psutil.disk_io_counters()
        last_activity_time = time.time()
        
        while self.is_running:
            time.sleep(0.1)
            
            # Procesar actualizaciones pendientes del menú
            self.process_pending_updates()
            
            try:
                current_stats = psutil.disk_io_counters()
                
                if current_stats and previous_stats:
                    read_bytes = current_stats.read_bytes - previous_stats.read_bytes
                    write_bytes = current_stats.write_bytes - previous_stats.write_bytes
                    
                    read_active = read_bytes > 5000
                    write_active = write_bytes > 5000
                    
                    if read_active or write_active:
                        self.activity_count += 1
                        last_activity_time = time.time()
                        self.activity_timeout = time.time() + 0.5
                        
                        icon_color, activity_type = self.determine_icon_color(read_active, write_active)
                        self.update_icon_color(activity_type)
                        
                        if read_active and write_active and self.sound_config['sound_triggers']['both']:
                            self.play_sound_by_type('both')
                        elif write_active and self.sound_config['sound_triggers']['write']:
                            self.play_sound_by_type('write')
                        elif read_active and self.sound_config['sound_triggers']['read']:
                            self.play_sound_by_type('read')
                    
                    elif time.time() > self.activity_timeout:
                        if self.current_status != "Inactivo":
                            self.update_icon_color("inactive")
                
                previous_stats = current_stats
                
            except Exception as e:
                logging.error(f"Error en monitoreo de disco: {e}")
                time.sleep(1)  # Esperar antes de reintentar
    
    def quit_program(self, icon=None, item=None):
        """Salir del programa"""
        logging.info("Saliendo del programa...")
        self.is_running = False
        self.save_config()
        
        if self.tray_icon:
            try:
                self.tray_icon.stop()
                logging.info("✅ Tray icon detenido")
            except Exception as e:
                logging.error(f"Error deteniendo tray icon: {e}")
        
        logging.info("✅ Programa finalizado correctamente")
        os._exit(0)
    
    def start(self):
        """Iniciar aplicación"""
        logging.info("Iniciando aplicación principal...")
        
        if not PSUTIL_AVAILABLE:
            logging.error("❌ psutil no disponible - no se puede iniciar")
            return
        
        if not PILLOW_AVAILABLE:
            logging.error("❌ pystray/PIL no disponibles - no se puede iniciar")
            return
        
        try:
            monitor_thread = threading.Thread(target=self.monitor_disk_activity, daemon=True)
            monitor_thread.start()
            logging.info("✅ Hilo de monitoreo iniciado")
            
            logging.info("✅ Iniciando loop principal del tray icon...")
            self.tray_icon.run()
            
        except Exception as e:
            logging.error(f"❌ ERROR CRÍTICO en start(): {e}")
            logging.error(traceback.format_exc())
        finally:
            self.quit_program()

def global_exception_handler(exc_type, exc_value, exc_traceback):
    """Manejador global de excepciones"""
    if issubclass(exc_type, KeyboardInterrupt):
        # Ignorar KeyboardInterrupt para permitir cierre normal
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logging.critical("❌ EXCEPCIÓN NO CAPTURADA:", exc_info=(exc_type, exc_value, exc_traceback))

# Configurar manejador global de excepciones
sys.excepthook = global_exception_handler

if __name__ == "__main__":
    try:
        logging.info("🚀 Iniciando aplicación HardDriveSimulator")
        app = HardDriveSimulator()
        app.start()
    except Exception as e:
        logging.critical(f"❌ ERROR CRÍTICO en main: {e}")
        logging.critical(traceback.format_exc())
        input("Presiona Enter para salir...")  # Para evitar cierre inmediato en .exe