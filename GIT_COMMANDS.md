# 📋 Comandos Git para GitHub - Paso a Paso

Este documento contiene todos los comandos necesarios para gestionar el proyecto en GitHub.

## 🚀 Configuración Inicial (Solo Primera Vez)

### 1. Inicializar Repositorio Local
```bash
# Inicializar git en el proyecto
git init

# Configurar información del usuario (si no está configurado globalmente)
git config user.name "Tu Nombre"
git config user.email "tu-email@example.com"
```

### 2. Agregar Archivos al Staging
```bash
# Ver el estado de los archivos
git status

# Agregar todos los archivos
git add .

# O agregar archivos específicos
git add README.md
git add src/
git add requirements.txt
```

### 3. Primer Commit
```bash
# Hacer el primer commit con mensaje descriptivo
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
- Licencia Apache 2.0"
```

### 4. Crear Repositorio en GitHub
```bash
# Crear repositorio público en GitHub usando GitHub CLI
gh repo create hardrivesound --public --source=. --description="🔊 Simulador de Sonido de Disco Duro Vintage - Reproduce sonidos de discos duros antiguos con monitorización en tiempo real"

# O mediante comandos git tradicionales (después de crear repo manualmente en GitHub)
git remote add origin https://github.com/TU-USUARIO/hardrivesound.git
```

### 5. Subir Cambios
```bash
# Ver las ramas disponibles
git branch

# Renombrar rama a 'main' si es necesario
git branch -M main

# Subir los cambios al repositorio remoto
git push -u origin main
```

## 🔄 Flujo de Trabajo Regular

### Hacer Cambios y Commit
```bash
# 1. Ver archivos modificados
git status

# 2. Agregar cambios
git add .

# 3. Hacer commit con mensaje descriptivo según tipo de cambio
git commit -m "tipo: descripción breve"
```

### Tipos de Commits (Conventional Commits)
- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Cambios en documentación
- `style:` Formateo, punto y coma, etc
- `refactor:` Refactorización de código
- `perf:` Mejoras de rendimiento
- `test:` Añadir o corregir tests
- `chore:` Mantenimiento, dependencias, etc

### Ejemplos de Commits
```bash
# Nueva característica
git commit -m "feat: Agregar soporte para volumen ajustable"

# Corrección de bug
git commit -m "fix: Corregir error al cargar iconos en Windows 7"

# Documentación
git commit -m "docs: Actualizar README con instrucciones de instalación"

# Mantenimiento
git commit -m "chore: Actualizar dependencias a última versión"
```

### Subir Cambios a GitHub
```bash
# Subir los cambios a la rama main
git push origin main
```

## 🏷️ Gestión de Versiones

### Incrementar Versión

#### 1. Actualizar Versión en el Código
Editar `src/__init__.py`:
```python
__version__ = "3.1.0"  # Incrementar según tipo de cambio
```

#### 2. Actualizar CHANGELOG.md
Agregar los cambios en `CHANGELOG.md`:
```markdown
## [3.1.0] - 2024-XX-XX

### ✨ Añadido
- Nueva funcionalidad X
- ...
```

#### 3. Commit de la Versión
```bash
# Agregar cambios
git add src/__init__.py CHANGELOG.md

# Commit siguiendo versionamiento semántico
git commit -m "chore: Bump version to 3.1.0"
```

#### 4. Subir a GitHub
```bash
# Subir a main - Esto automáticamente creará un release via GitHub Actions
git push origin main
```

## 📊 Versionamiento Semántico

### Formato: MAJOR.MINOR.PATCH (ejemplo: 3.0.0)

#### Incrementar MAJOR (3.0.0 → 4.0.0)
- Cambios incompatibles en la API
- Rediseños completos
- Cambios que rompen compatibilidad

```bash
# Ejemplo: De v3.0.0 a v4.0.0
# Editar __version__ = "4.0.0" en src/__init__.py
git add src/__init__.py CHANGELOG.md
git commit -m "chore: Bump version to 4.0.0 - Breaking changes"
git push origin main
```

#### Incrementar MINOR (3.0.0 → 3.1.0)
- Nueva funcionalidad
- Mejoras compatibles
- Nuevas características

```bash
# Ejemplo: De v3.0.0 a v3.1.0
# Editar __version__ = "3.1.0" en src/__init__.py
git add src/__init__.py CHANGELOG.md
git commit -m "chore: Bump version to 3.1.0 - New features"
git push origin main
```

#### Incrementar PATCH (3.0.0 → 3.0.1)
- Correcciones de bugs
- Fixes menores
- Mejoras de rendimiento

```bash
# Ejemplo: De v3.0.0 a v3.0.1
# Editar __version__ = "3.0.1" en src/__init__.py
git add src/__init__.py CHANGELOG.md
git commit -m "chore: Bump version to 3.0.1 - Bug fixes"
git push origin main
```

## 🤖 Release Automático

### Funcionamiento
1. Modificas `__version__` en `src/__init__.py`
2. Haces commit y push a `main`
3. GitHub Actions automáticamente:
   - Detecta la nueva versión
   - Compila el ejecutable
   - Crea el paquete ZIP
   - Genera el changelog
   - Crea un release en GitHub con el tag vX.Y.Z

### Verificar Release
```bash
# Ver tags locales
git tag

# Ver tags remotos
git ls-remote --tags origin

# Ver releases en GitHub
gh release list

# Ver detalles de un release específico
gh release view v3.0.0
```

## 📝 Comandos Útiles

### Ver Historial
```bash
# Ver historial de commits
git log --oneline --graph --all

# Ver cambios recientes
git log -5 --pretty=format:"%h - %an, %ar : %s"

# Ver diferencias
git diff
```

### Sincronizar con GitHub
```bash
# Descargar cambios del remoto
git fetch origin

# Ver estado comparado con remoto
git status

# Descargar e integrar cambios
git pull origin main
```

### Administración de Branches
```bash
# Ver ramas
git branch -a

# Crear nueva rama
git checkout -b feature/nueva-funcionalidad

# Cambiar de rama
git checkout main

# Fusionar rama
git merge feature/nueva-funcionalidad
```

### Deshacer Cambios
```bash
# Deshacer cambios no commiteados en un archivo
git checkout -- archivo.py

# Deshacer último commit (mantener cambios)
git reset --soft HEAD~1

# Deshacer último commit (descartar cambios)
git reset --hard HEAD~1
```

## 🎯 Flujo Completo para Nueva Versión

### Ejemplo: Agregar nueva funcionalidad (v3.0.0 → v3.1.0)

```bash
# 1. Hacer cambios en el código
# ... editar archivos ...

# 2. Probar cambios
python main.py

# 3. Actualizar versión
# Editar src/__init__.py: __version__ = "3.1.0"

# 4. Actualizar CHANGELOG.md
# Agregar entrada para [3.1.0]

# 5. Agregar cambios
git add .

# 6. Commit descriptivo
git commit -m "feat: Agregar control de volumen individual

- Slider de volumen para cada tipo de sonido
- Guardar preferencias de volumen
- UI mejorada en menú de bandeja

Version bump: 3.0.0 → 3.1.0"

# 7. Subir a GitHub
git push origin main

# 8. Esperar a que GitHub Actions cree el release automáticamente
# Verificar en: https://github.com/TU-USUARIO/hardrivesound/releases
```

## 🔍 Verificación de Estado

```bash
# Ver estado completo del repositorio
git status

# Ver configuración del repositorio
git config --list

# Ver remotes configurados
git remote -v

# Verificar conexión con GitHub
gh auth status
```

## 📚 Recursos

- [Git Documentation](https://git-scm.com/doc)
- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)

---

**Nota**: Este proyecto usa versionamiento automático. Cada push a `main` con una nueva versión en `src/__init__.py` generará automáticamente un release en GitHub con el ejecutable compilado.
