@echo off
chcp 65001 >nul
echo 🚀 Compilando Simulador Disco Duro - TODO EN UNO...
echo.

pyinstaller --onefile --windowed --name "hardrive" --add-data "config.json;." --add-data "sounds/*;sounds" --add-data "hdd_seek.wav;." --icon "hardrive.ico" --hidden-import "pystray._win32" --hidden-import "pystray._util" --hidden-import "PIL._imaging" --hidden-import "psutil" --clean hardrive.py

echo.
echo ✅ ¡Compilación completada!
echo 📂 Ejecutable: dist\hardrive.exe
echo 📏 Tamaño aproximado: ~15-20 MB
echo.
echo 🎯 Este .exe contiene TODO:
echo    • La aplicación
echo    • Configuración
echo    • Sonidos incluidos
echo    • Icono personalizado
echo.
pause