"""
Sistema de logging para el simulador de disco duro.
Proporciona configuración centralizada de logs.
"""
import logging
import os
import sys
import platform
from typing import Optional


class AppLogger:
    """Gestor de logging para la aplicación"""
    
    _instance: Optional['AppLogger'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'AppLogger':
        """Patrón Singleton para el logger"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializar el logger (solo una vez)"""
        if not AppLogger._initialized:
            self.logger = logging.getLogger("HardDriveSimulator")
            self.base_dir = self._get_base_dir()
            self.log_file = os.path.join(self.base_dir, 'hdd_simulator.log')
            self._setup_logging()
            AppLogger._initialized = True
    
    def _get_base_dir(self) -> str:
        """Obtener directorio base de la aplicación"""
        is_compiled = getattr(sys, 'frozen', False)
        if is_compiled:
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    def _setup_logging(self) -> None:
        """Configurar el sistema de logging"""
        try:
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(self.log_file, encoding='utf-8'),
                    logging.StreamHandler()
                ]
            )
            
            self.info("=" * 60)
            self.info("INICIANDO SIMULADOR DE DISCO DURO VINTAGE")
            self.info("=" * 60)
            self.info(f"Directorio base: {self.base_dir}")
            self.info(f"Archivo log: {self.log_file}")
            self.info(f"Python: {platform.python_version()}")
            self.info(f"Sistema: {platform.system()} {platform.release()}")
            self.info(f"Compilado: {getattr(sys, 'frozen', False)}")
        except Exception as e:
            print(f"ERROR CRÍTICO configurando log: {e}")
    
    def debug(self, message: str) -> None:
        """Log nivel DEBUG"""
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """Log nivel INFO"""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log nivel WARNING"""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log nivel ERROR"""
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """Log nivel CRITICAL"""
        self.logger.critical(message)


# Instancia global del logger
logger = AppLogger()
