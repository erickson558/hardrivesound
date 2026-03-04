"""
Monitor de actividad del disco duro.
Monitorea la actividad de lectura/escritura del disco en tiempo real.
"""
import time
from typing import Optional, Tuple, Callable
from src.utils.logger import logger
from src.utils.constants import (
    MIN_ACTIVITY_THRESHOLD,
    MONITOR_INTERVAL,
    ACTIVITY_TIMEOUT,
    ACTIVITY_TYPE_READ,
    ACTIVITY_TYPE_WRITE,
    ACTIVITY_TYPE_BOTH,
    ACTIVITY_TYPE_INACTIVE
)

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.error("❌ psutil no disponible")


class DiskMonitor:
    """Monitor de actividad del disco duro"""
    
    def __init__(self, icon_behavior: str = 'write_priority'):
        """
        Inicializar monitor de disco.
        
        Args:
            icon_behavior: Comportamiento del icono (write_priority, read_priority, both_green)
        """
        self.is_running = True
        self.icon_behavior = icon_behavior
        self.activity_count = 0
        self.activity_timeout = 0.0
        self.on_activity_callback: Optional[Callable] = None
        self.on_icon_update_callback: Optional[Callable] = None
        
        if not PSUTIL_AVAILABLE:
            logger.error("❌ DiskMonitor no puede funcionar sin psutil")
    
    def set_icon_behavior(self, behavior: str) -> None:
        """
        Actualizar comportamiento del icono.
        
        Args:
            behavior: Nuevo comportamiento
        """
        self.icon_behavior = behavior
    
    def set_activity_callback(self, callback: Callable) -> None:
        """
        Establecer callback para actividad detectada.
        
        Args:
            callback: Función a llamar cuando hay actividad
        """
        self.on_activity_callback = callback
    
    def set_icon_update_callback(self, callback: Callable) -> None:
        """
        Establecer callback para actualización de icono.
        
        Args:
            callback: Función a llamar para actualizar icono
        """
        self.on_icon_update_callback = callback
    
    def determine_activity_type(self, read_active: bool, write_active: bool) -> Tuple[str, str]:
        """
        Determinar tipo de actividad y color de icono.
        
        Args:
            read_active: Si hay actividad de lectura
            write_active: Si hay actividad de escritura
            
        Returns:
            Tupla (color, tipo_actividad)
        """
        if read_active and write_active:
            if self.icon_behavior == 'both_green':
                return ("green", ACTIVITY_TYPE_BOTH)
            elif self.icon_behavior == 'read_priority':
                return ("green", ACTIVITY_TYPE_READ)
            else:  # write_priority
                return ("red", ACTIVITY_TYPE_WRITE)
        elif write_active:
            return ("red", ACTIVITY_TYPE_WRITE)
        elif read_active:
            return ("green", ACTIVITY_TYPE_READ)
        else:
            return ("gray", ACTIVITY_TYPE_INACTIVE)
    
    def monitor_loop(self) -> None:
        """
        Bucle principal de monitoreo.
        Monitorea continuamente la actividad del disco.
        """
        if not PSUTIL_AVAILABLE:
            logger.error("No se puede monitorear - psutil no disponible")
            return
        
        logger.info("🔍 Iniciando monitoreo de disco...")
        previous_stats = psutil.disk_io_counters()
        
        while self.is_running:
            time.sleep(MONITOR_INTERVAL)
            
            try:
                current_stats = psutil.disk_io_counters()
                
                if current_stats and previous_stats:
                    # Calcular diferencias
                    read_bytes = current_stats.read_bytes - previous_stats.read_bytes
                    write_bytes = current_stats.write_bytes - previous_stats.write_bytes
                    
                    # Determinar si hay actividad significativa
                    read_active = read_bytes > MIN_ACTIVITY_THRESHOLD
                    write_active = write_bytes > MIN_ACTIVITY_THRESHOLD
                    
                    if read_active or write_active:
                        self.activity_count += 1
                        self.activity_timeout = time.time() + ACTIVITY_TIMEOUT
                        
                        # Determinar tipo de actividad
                        icon_color, activity_type = self.determine_activity_type(
                            read_active, write_active
                        )
                        
                        # Notificar actividad
                        if self.on_activity_callback:
                            self.on_activity_callback(activity_type)
                        
                        # Actualizar icono
                        if self.on_icon_update_callback:
                            self.on_icon_update_callback(activity_type)
                    
                    # Verificar timeout de inactividad
                    elif time.time() > self.activity_timeout:
                        if self.on_icon_update_callback:
                            self.on_icon_update_callback(ACTIVITY_TYPE_INACTIVE)
                
                previous_stats = current_stats
            
            except Exception as e:
                logger.error(f"❌ Error en monitor de disco: {e}")
                time.sleep(1)
    
    def stop(self) -> None:
        """Detener el monitoreo"""
        logger.info("⏹️ Deteniendo monitor de disco...")
        self.is_running = False
