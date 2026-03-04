"""
Punto de entrada principal de la aplicación.
Hard Drive Sound Simulator - Simulador de Sonido de Disco Duro Vintage
"""
from src.app import HardDriveSimulator
from src.utils.logger import logger


def main():
    """Función principal"""
    try:
        logger.info("=" * 60)
        logger.info("INICIANDO APLICACIÓN")
        logger.info("=" * 60)
        
        app = HardDriveSimulator()
        app.start()
        
    except Exception as e:
        logger.critical(f"❌ ERROR CRÍTICO: {e}")
        import traceback
        logger.critical(traceback.format_exc())
        input("Presiona Enter para salir...")


if __name__ == "__main__":
    main()
