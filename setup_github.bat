@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════════
echo   Configuración de GitHub - Hard Drive Sound Simulator
echo ═══════════════════════════════════════════════════════════
echo.

echo [1/7] Verificando Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git no está instalado. Instala Git desde: https://git-scm.com/
    pause
    exit /b 1
)
echo ✅ Git encontrado

echo.
echo [2/7] Inicializando repositorio Git...
if exist ".git" (
    echo ⚠️ Repositorio ya existe, limpiando...
    rmdir /s /q .git
)
git init
echo ✅ Repositorio inicializado

echo.
echo [3/7] Configurando usuario Git...
git config user.email "erickson@hardrivesound.com"
git config user.name "Erickson"
echo ✅ Usuario configurado

echo.
echo [4/7] Agregando archivos al staging...
git add .
echo ✅ Archivos agregados

echo.
echo [5/7] Creando commit inicial...
git commit -m "feat: Refactorización completa v3.0.0 - Separación backend/frontend

- Arquitectura modular con separación de responsabilidades
- Backend: ConfigManager, AudioEngine, DiskMonitor
- Frontend: TrayInterface, IconGenerator
- Modelos de datos con dataclasses
- Sistema de logging mejorado
- Constantes centralizadas
- Type hints completos
- Documentación exhaustiva
- GitHub Actions para releases automáticos
- Licencia Apache 2.0

BREAKING CHANGE: Nueva estructura de proyecto requiere Python 3.8+"
echo ✅ Commit creado

echo.
echo [6/7] Creando repositorio en GitHub...
echo.
echo Por favor, elige una opción:
echo   1) Crear con GitHub CLI (gh) - Recomendado
echo   2) Configurar manualmente
echo.
choice /c 12 /n /m "Selecciona [1 o 2]: "

if errorlevel 2 goto MANUAL
if errorlevel 1 goto GHCLI

:GHCLI
echo.
echo Verificando GitHub CLI...
gh --version >nul 2>&1
if errorlevel 1 (
    echo ❌ GitHub CLI no está instalado
    echo Instala desde: https://cli.github.com/
    echo.
    echo Continuando con configuración manual...
    goto MANUAL
)

echo ✅ GitHub CLI encontrado
echo.
echo Creando repositorio público en GitHub...
gh repo create hardrivesound --public --source=. --description="🔊 Simulador de Sonido de Disco Duro Vintage - Reproduce sonidos de discos duros antiguos con monitorización en tiempo real"

if errorlevel 1 (
    echo ❌ Error creando repositorio en GitHub
    echo Verifica que estés autenticado con: gh auth login
    pause
    exit /b 1
)

echo ✅ Repositorio creado en GitHub
goto PUSH

:MANUAL
echo.
echo ═══════════════════════════════════════════════════════════
echo   CONFIGURACIÓN MANUAL
echo ═══════════════════════════════════════════════════════════
echo.
echo 1. Ve a: https://github.com/new
echo 2. Nombre del repositorio: hardrivesound
echo 3. Descripción: 🔊 Simulador de Sonido de Disco Duro Vintage
echo 4. Visibilidad: Public
echo 5. NO inicialices con README, .gitignore, o license
echo 6. Click "Create repository"
echo.
pause

set /p GITHUB_USER="Ingresa tu usuario de GitHub: "
echo.
echo Configurando remote...
git remote add origin https://github.com/%GITHUB_USER%/hardrivesound.git
echo ✅ Remote configurado

:PUSH
echo.
echo [7/7] Subiendo cambios a GitHub...
git branch -M main
git push -u origin main

if errorlevel 1 (
    echo.
    echo ❌ Error al subir a GitHub
    echo.
    echo Posibles soluciones:
    echo 1. Verifica tus credenciales de GitHub
    echo 2. Si usas 2FA, necesitas un Personal Access Token
    echo 3. Configura con: git credential manager
    echo.
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════════════════════
echo   ✅ ¡CONFIGURACIÓN COMPLETADA!
echo ═══════════════════════════════════════════════════════════
echo.
echo 📦 Repositorio: https://github.com/%GITHUB_USER%/hardrivesound
echo 🏷️ Versión inicial: v3.0.0
echo 🤖 GitHub Actions configurado para releases automáticos
echo.
echo PRÓXIMOS PASOS:
echo.
echo 1. Verifica el repositorio en GitHub
echo 2. El primer release se creará automáticamente
echo 3. Para nuevas versiones:
echo    a) Edita src/__init__.py con nueva versión
echo    b) Actualiza CHANGELOG.md
echo    c) git add . && git commit -m "chore: Bump version to X.Y.Z"
echo    d) git push origin main
echo.
echo 📚 Lee GIT_COMMANDS.md para guía completa
echo.
pause
