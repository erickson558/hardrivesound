# Changelog

Todos los cambios notables del proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/),
y este proyecto adhiere a [Versionamiento Semántico](https://semver.org/spec/v2.0.0.html).

## [3.0.1] - 2026-03-03

### 🔧 Cambiado
- Corrección de sintaxis del workflow `.github/workflows/release.yml`
- Compilación ajustada para generar `hardrive.exe` en la carpeta raíz del proyecto
- Pipeline de release alineado para push a `main`

### 📚 Documentación
- README y configuración actualizados a versión `3.0.1`

## [3.0.0] - 2024-XX-XX

### 🎉 Rediseño Completo - Separación Backend/Frontend

#### ✨ Añadido
- Arquitectura modular separando backend y frontend
- Sistema de logging mejorado con patrón Singleton
- Modelos de datos usando dataclasses
- Constantes centralizadas para mejor mantenimiento
- Type hints en todas las funciones
- Documentación completa con docstrings
- Sistema de versionamiento centralizado
- GitHub Actions para releases automáticos
- README completo con badges y documentación
- Licencia Apache 2.0

#### 🔧 Cambiado
- Estructura del proyecto completamente refactorizada
- Mejor separación de responsabilidades
- ConfigManager separado para gestión de configuración
- AudioEngine independiente para reproducción de sonidos
- DiskMonitor modular para monitoreo del disco
- TrayInterface mejorado con callbacks
- IconGenerator con 4 estilos diferentes

#### 🐛 Corregido
- Mejor manejo de errores en todos los componentes
- Gestión de recursos más eficiente
- Logging más robusto

#### 📚 Documentación
- README completo en español
- Documentación de arquitectura
- Guía de contribución
- Changelog estructurado

## [2.1.1] - 2024-XX-XX

### 🔄 Versión Anterior (Monolítica)

#### Características
- Monitorización básica de disco
- Reproducción de sonidos vintage
- Icono en bandeja del sistema
- Configuración JSON

---

### Guía de Versionamiento

El proyecto sigue [Versionamiento Semántico](https://semver.org/):

- **MAJOR** (X.0.0): Cambios incompatibles en la API
- **MINOR** (x.X.0): Nueva funcionalidad compatible hacia atrás
- **PATCH** (x.x.X): Correcciones de bugs compatibles hacia atrás

### Tipos de Cambios

- `✨ Añadido` - Nueva funcionalidad
- `🔧 Cambiado` - Cambios en funcionalidad existente
- `🗑️ Deprecado` - Funcionalidad que será removida
- `🔥 Removido` - Funcionalidad removida
- `🐛 Corregido` - Corrección de bugs
- `🔒 Seguridad` - Fixes de seguridad
- `📚 Documentación` - Cambios en documentación
