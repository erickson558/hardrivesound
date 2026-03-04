# Hard Drive Sound Simulator 🔊

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

**Simulador de Sonido de Disco Duro Vintage** - Una aplicación de escritorio que reproduce sonidos de discos duros antiguos basándose en la actividad real del disco en tiempo real.

![Version](https://img.shields.io/badge/version-3.0.0-green.svg)

## 📋 Características

- 🔍 **Monitorización en Tiempo Real**: Detecta automáticamente actividad de lectura/escritura del disco
- 🔊 **Sonidos Vintage Auténticos**: Reproduce sonidos característicos de discos duros antiguos
- 🎨 **4 Estilos de Iconos**: Modern, Classic, Simple y Retro
- ⚙️ **Altamente Configurable**: Controla todos los aspectos desde el menú de la bandeja
- 💾 **Configuración Persistente**: Tus preferencias se guardan automáticamente
- 🎯 **Ligero y Eficiente**: Consumo mínimo de recursos
- 🪟 **Integración con Windows**: Se ejecuta en la bandeja del sistema

## 🚀 Inicio Rápido

### Usando el Ejecutable (Recomendado)

1. Descarga el último release desde [Releases](https://github.com/erickson558/hardrivesound/releases)
2. Extrae el contenido del ZIP
3. Ejecuta `HardDriveSoundSimulator.exe`
4. ¡Disfruta de los sonidos nostálgicos!

### Desde el Código Fuente

#### Requisitos Previos

- Python 3.8 o superior
- Windows OS (debido a la dependencia de `winsound`)

#### Instalación

```bash
# Clonar el repositorio
git clone https://github.com/erickson558/hardrivesound.git
cd hardrivesound

# Crear entorno virtual (recomendado)
python -m venv venv
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python main.py
```

## 🎮 Uso

### Menú de la Bandeja del Sistema

Haz clic derecho en el icono de la bandeja para acceder a:

#### 🎛️ Configuración Global
- **Sonido Global**: Activa/desactiva todos los sonidos
- **Delay**: Ajusta el tiempo entre sonidos (0.5s - 5s)
- **Comportamiento del Icono**: Cambia la prioridad de visualización
- **Estilo del Icono**: Alterna entre Modern, Classic, Simple y Retro

#### 🔊 Triggers de Sonido
- **Solo Lectura**: Reproduce sonido solo en lecturas
- **Solo Escritura**: Reproduce sonido solo en escrituras
- **Lectura+Escritura**: Reproduce sonido en ambas actividades (recomendado)

#### 📖 Sonidos Individuales
- Activa/desactiva cada tipo de sonido independientemente
- Personaliza qué sonidos se reproducen

### Indicadores de Estado

El icono cambia de color según la actividad:
- 🟢 **Verde**: Actividad de lectura
- 🔴 **Rojo**: Actividad de escritura
- 🟡 **Amarillo**: Actividad mixta
- ⚫ **Gris**: Sin actividad

## 🏗️ Arquitectura del Proyecto

```
hardrivesound/
│
├── src/
│   ├── __init__.py              # Versión y metadata
│   ├── app.py                   # Aplicación principal
│   │
│   ├── backend/                 # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── config_manager.py    # Gestión de configuración
│   │   ├── audio_engine.py      # Motor de audio
│   │   └── disk_monitor.py      # Monitor de disco
│   │
│   ├── frontend/                # Interfaz de usuario
│   │   ├── __init__.py
│   │   ├── tray_interface.py    # Interfaz de bandeja
│   │   └── icon_generator.py    # Generador de iconos
│   │
│   ├── models/                  # Modelos de datos
│   │   ├── __init__.py
│   │   └── config_model.py      # Modelo de configuración
│   │
│   └── utils/                   # Utilidades
│       ├── __init__.py
│       ├── constants.py         # Constantes globales
│       └── logger.py            # Sistema de logging
│
├── sounds/                      # Archivos de audio
│   ├── hdd_seek.wav
│   ├── hdd_click.wav
│   └── hdd_spin.wav
│
├── main.py                      # Punto de entrada
├── config.json                  # Configuración del usuario
├── requirements.txt             # Dependencias
├── build.bat                    # Script de compilación
├── hardrive.ico                 # Icono de la aplicación
└── README.md                    # Este archivo
```

## 🔧 Compilación

Para crear tu propio ejecutable:

```bash
# Instalar PyInstaller
pip install pyinstaller

# Ejecutar script de compilación
build.bat

# El ejecutable estará en dist/HardDriveSoundSimulator.exe
```

## 📝 Configuración

La configuración se guarda en `config.json` y se carga automáticamente al iniciar:

```json
{
  "version": "3.0.0",
  "enabled": true,
  "global_delay": 1.0,
  "icon_behavior": "write_priority",
  "sound_triggers": {
    "read": false,
    "write": false,
    "both": true
  },
  "sounds": {
    "read": {
      "enabled": true,
      "file": "hdd_seek.wav",
      "volume": 100
    },
    "write": {
      "enabled": true,
      "file": "hdd_click.wav",
      "volume": 100
    },
    "both": {
      "enabled": true,
      "file": "hdd_spin.wav",
      "volume": 100
    }
  }
}
```

## 🤝 Contribuir

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está licenciado bajo la Apache License 2.0 - ver el archivo [LICENSE](LICENSE) para más detalles.

## 👤 Autor

**Erickson**

## 🙏 Agradecimientos

- Comunidad de Python por las excelentes librerías
- Usuarios que contribuyen con feedback y mejoras
- Todos los que extrañan el sonido de los viejos discos duros 🔊

## 📚 Dependencias

- **psutil**: Monitoreo de sistema y disco
- **Pillow (PIL)**: Generación de iconos
- **pystray**: Icono de bandeja del sistema
- **PyInstaller**: Compilación a ejecutable

## 🐛 Reportar Problemas

Si encuentras un bug o tienes una sugerencia, por favor abre un [Issue](https://github.com/erickson558/hardrivesound/issues).

## 📈 Roadmap

- [ ] Soporte para sonidos personalizados
- [ ] Control de volumen individual
- [ ] Exportar/importar configuraciones
- [ ] Estadísticas de uso del disco
- [ ] Tema oscuro/claro para el menú

## ⚙️ Requisitos del Sistema

- **SO**: Windows 10/11 (7/8 pueden funcionar)
- **RAM**: 50 MB mínimo
- **Disco**: 20 MB
- **Python**: 3.8+ (solo para desarrollo)

---

<div align="center">
  
**¿Te gusta el proyecto? ¡Dale una ⭐!**

Made with ❤️ and nostalgia

</div>
