@echo off
chcp 65001 >nul
echo 🚀 Compilando Hard Drive Sound Simulator v3.0.0...
echo.

REM Limpiar builds anteriores
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo 📦 Empaquetando con PyInstaller...
pyinstaller --onefile ^
    --windowed ^
    --name "HardDriveSoundSimulator" ^
    --icon "hardrive.ico" ^
    --add-data "config.json;." ^
    --add-data "sounds;sounds" ^
    --add-data "*.wav;." ^
    --hidden-import "pystray._win32" ^
    --hidden-import "pystray._util" ^
    --hidden-import "PIL._imaging" ^
    --hidden-import "psutil" ^
    --clean ^
    main.py

echo.
echo ✅ ¡Compilación completada!
echo 📂 Ejecutable: dist\HardDriveSoundSimulator.exe
echo.
echo 🎯 El .exe incluye:
echo    • La aplicación completa
echo    • Configuración
echo    • Sonidos incluidos
echo    • Icono personalizado
echo.
pause
