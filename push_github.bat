@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════════
echo   Subir cambios a GitHub
echo ═══════════════════════════════════════════════════════════
echo.

echo Cambiando rama a main...
git branch -M main

echo.
echo Subiendo cambios a GitHub...
git push -u origin main

if errorlevel 1 (
    echo.
    echo ❌ Error al subir cambios
    pause
    exit /b 1
)

echo.
echo ✅ ¡Cambios subidos exitosamente!
echo.
echo Repositorio: https://github.com/erickson558/hardrivesound
echo.
pause
