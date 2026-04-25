"""
Generador de sonidos mecanicos sinteticos para HDD.
Crea archivos WAV mono de 16-bit sin depender de samples externos.
"""
import math
import os
import random
import struct
import wave
from typing import Callable, Dict, List, Tuple

from src.utils.logger import logger


SAMPLE_RATE = 22050
MAX_AMPLITUDE = 32767

DEFAULT_HDD_SOUNDS = {
    "hdd_seek.wav": ("seek", 0.13),
    "hdd_click.wav": ("click", 0.07),
    "hdd_spin.wav": ("spin", 0.22),
}


def _clamp(sample: float) -> int:
    """Convertir muestra float [-1, 1] a int16."""
    if sample > 1.0:
        sample = 1.0
    if sample < -1.0:
        sample = -1.0
    return int(sample * MAX_AMPLITUDE)


def _write_wav(path: str, samples: List[float]) -> None:
    """Escribir muestras PCM16 mono a disco."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with wave.open(path, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        frames = b"".join(struct.pack("<h", _clamp(s)) for s in samples)
        wav.writeframes(frames)


def _decay_envelope(t: float, duration: float) -> float:
    """Envolvente exponencial suave para transientes mecanicos."""
    if duration <= 0:
        return 0.0
    k = 6.0 / duration
    return math.exp(-k * t)


def _apply_fades(samples: List[float], fade_in_ms: float = 7.0, fade_out_ms: float = 18.0) -> List[float]:
    """Aplicar fade in/out suave para evitar clics en bordes de onda."""
    if not samples:
        return samples

    total = len(samples)
    fade_in_n = max(1, int(SAMPLE_RATE * (fade_in_ms / 1000.0)))
    fade_out_n = max(1, int(SAMPLE_RATE * (fade_out_ms / 1000.0)))
    fade_in_n = min(fade_in_n, total)
    fade_out_n = min(fade_out_n, total)

    out = samples[:]

    for i in range(fade_in_n):
        gain = i / max(1, fade_in_n - 1)
        out[i] *= gain

    for i in range(fade_out_n):
        idx = total - fade_out_n + i
        gain = 1.0 - (i / max(1, fade_out_n - 1))
        out[idx] *= max(0.0, gain)

    return out


def _fade_profile_params(profile: str, sound_key: str) -> Tuple[float, float]:
    """Retornar tiempos de fade por perfil para cada tipo de sonido."""
    if profile == "soft":
        table = {
            "seek": (9.0, 24.0),
            "click": (7.0, 20.0),
            "spin": (12.0, 30.0),
        }
    elif profile == "aggressive":
        table = {
            "seek": (2.5, 10.0),
            "click": (1.8, 8.0),
            "spin": (4.0, 14.0),
        }
    else:
        table = {
            "seek": (5.0, 16.0),
            "click": (3.0, 14.0),
            "spin": (8.0, 22.0),
        }
    return table.get(sound_key, (7.0, 18.0))


def _generate_seek_sound(duration: float = 0.13, fade_profile: str = "balanced") -> List[float]:
    """Seek: click breve con ruido y cola corta."""
    total = int(SAMPLE_RATE * duration)
    samples: List[float] = []

    for n in range(total):
        t = n / SAMPLE_RATE
        base = math.sin(2 * math.pi * 1200 * t)
        noise = random.uniform(-1.0, 1.0)
        env = _decay_envelope(t, duration)
        pulse = 1.0 if n < int(SAMPLE_RATE * 0.003) else 0.0
        value = (0.40 * base + 0.45 * noise + 0.8 * pulse) * env
        samples.append(value * 0.55)

    fade_in, fade_out = _fade_profile_params(fade_profile, "seek")
    return _apply_fades(samples, fade_in_ms=fade_in, fade_out_ms=fade_out)


def _generate_click_sound(duration: float = 0.07, fade_profile: str = "balanced") -> List[float]:
    """Click de actuador: mas corto y seco."""
    total = int(SAMPLE_RATE * duration)
    samples: List[float] = []

    for n in range(total):
        t = n / SAMPLE_RATE
        noise = random.uniform(-1.0, 1.0)
        tone = math.sin(2 * math.pi * 1800 * t)
        env = _decay_envelope(t, duration)
        transient = 1.0 if n < int(SAMPLE_RATE * 0.002) else 0.0
        value = (0.70 * noise + 0.20 * tone + 1.1 * transient) * env
        samples.append(value * 0.65)

    fade_in, fade_out = _fade_profile_params(fade_profile, "click")
    return _apply_fades(samples, fade_in_ms=fade_in, fade_out_ms=fade_out)


def _generate_spin_sound(duration: float = 0.22, fade_profile: str = "balanced") -> List[float]:
    """Lectura/escritura mixta: zumbido mecanico con jitter."""
    total = int(SAMPLE_RATE * duration)
    samples: List[float] = []

    for n in range(total):
        t = n / SAMPLE_RATE
        # Tono base del motor con leve modulacion.
        wobble = 6.0 * math.sin(2 * math.pi * 9 * t)
        motor_freq = 240 + wobble
        motor = math.sin(2 * math.pi * motor_freq * t)

        # Ruido mecanico filtrado de forma simple.
        hiss = random.uniform(-1.0, 1.0) * 0.35

        env = 0.65 + 0.35 * _decay_envelope(t, duration)
        value = (0.55 * motor + hiss) * env
        samples.append(value * 0.45)

    fade_in, fade_out = _fade_profile_params(fade_profile, "spin")
    return _apply_fades(samples, fade_in_ms=fade_in, fade_out_ms=fade_out)


def _get_builder_map() -> Dict[str, Callable[[float, str], List[float]]]:
    """Mapa de constructores de sonido por tipo lógico."""
    return {
        "seek": _generate_seek_sound,
        "click": _generate_click_sound,
        "spin": _generate_spin_sound,
    }


def _build_variant_filename(filename: str, variant_index: int) -> str:
    """Construir nombre de variante: hdd_seek.wav -> hdd_seek_v1.wav."""
    name, ext = os.path.splitext(filename)
    return f"{name}_v{variant_index}{ext}"


def get_existing_variant_files(base_dir: str, filename: str, variants: int = 8) -> List[str]:
    """Obtener lista de variantes existentes para un sonido base."""
    available: List[str] = []

    base_path = os.path.join(base_dir, filename)
    if os.path.exists(base_path):
        available.append(filename)

    for i in range(1, variants + 1):
        variant_name = _build_variant_filename(filename, i)
        variant_path = os.path.join(base_dir, variant_name)
        if os.path.exists(variant_path):
            available.append(variant_name)

    return available


def generate_missing_hdd_sounds(base_dir: str, variants: int = 8, fade_profile: str = "balanced") -> None:
    """
    Generar sonidos mecanicos por defecto si no existen.

    Los archivos se crean en la carpeta base para mantener compatibilidad
    con la configuracion actual del proyecto.
    """
    builders = _get_builder_map()

    for filename, (sound_key, base_duration) in DEFAULT_HDD_SOUNDS.items():
        builder = builders[sound_key]
        target = os.path.join(base_dir, filename)
        if not os.path.exists(target):
            try:
                logger.warning(f"Sonido faltante detectado. Generando: {filename}")
                samples = builder(base_duration, fade_profile=fade_profile)
                _write_wav(target, samples)
                logger.info(f"Sonido sintetico creado: {target}")
            except Exception as e:
                logger.error(f"No se pudo generar {filename}: {e}")

        # Generar variantes para reducir la sensación de bucle repetitivo.
        for i in range(1, variants + 1):
            variant_name = _build_variant_filename(filename, i)
            variant_path = os.path.join(base_dir, variant_name)
            if os.path.exists(variant_path):
                continue

            try:
                # Variación leve de duración para comportamiento más orgánico.
                variant_duration = base_duration * random.uniform(0.82, 1.18)
                samples = builder(variant_duration, fade_profile=fade_profile)
                _write_wav(variant_path, samples)
            except Exception as e:
                logger.error(f"No se pudo generar variante {variant_name}: {e}")


def apply_fade_to_wav(base_dir: str, filename: str, fade_in_ms: float, fade_out_ms: float) -> bool:
    """
    Aplica fade in/out coseno a un archivo WAV usando su copia .bak como master.

    Soporta:
      - PCM 16-bit mono (archivos sinteticos generados internamente)
      - IEEE Float32 estereo (grabaciones reales como hdd_seek.wav)

    El .bak se crea automaticamente la primera vez para permitir reaplicar
    distintos valores sin degradacion acumulativa.
    """
    # Importacion local para no requerir numpy en todo el modulo
    try:
        import numpy as np
        import shutil
    except ImportError:
        logger.error("numpy es requerido para apply_fade_to_wav")
        return False

    path = os.path.join(base_dir, filename)
    bak_path = path + ".bak"

    if not os.path.exists(path):
        logger.warning(f"apply_fade_to_wav: archivo no encontrado: {path}")
        return False

    try:
        # Crear backup master la primera vez para evitar degradacion acumulativa
        if not os.path.exists(bak_path):
            shutil.copy2(path, bak_path)
            logger.info(f"Backup master creado: {bak_path}")

        # Siempre leer desde el master para reaplicar con nuevos valores
        with open(bak_path, "rb") as f:
            raw = bytearray(f.read())

        # Localizar chunks fmt y data en el RIFF
        offset = 12
        fmt_offset = data_offset = -1
        data_size = 0
        while offset < len(raw) - 8:
            chunk_id   = bytes(raw[offset:offset + 4])
            chunk_size = struct.unpack_from("<I", raw, offset + 4)[0]
            if chunk_id == b"fmt ":
                fmt_offset = offset + 8
            elif chunk_id == b"data":
                data_offset = offset + 8
                data_size   = chunk_size
                break
            offset += 8 + chunk_size + (chunk_size % 2)

        if fmt_offset < 0 or data_offset < 0:
            logger.error(f"apply_fade_to_wav: WAV malformado en {filename}")
            return False

        # Leer campos del chunk fmt
        w_format, n_channels, sample_rate, _, _, bits = struct.unpack_from("<HHIIHH", raw, fmt_offset)
        audio_bytes = bytes(raw[data_offset: data_offset + data_size])

        # Convertir a float64 para procesado interno
        if w_format == 3 and bits == 32:
            # IEEE Float32 (grabaciones reales, e.g. hdd_seek.wav 96 kHz)
            samples = np.frombuffer(audio_bytes, dtype=np.float32).astype(np.float64).copy()
        elif w_format == 1 and bits == 16:
            # PCM 16-bit (sinteticos generados con _write_wav)
            samples = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float64) / 32767.0
        else:
            logger.warning(f"Formato WAV no soportado para fade: format={w_format} bits={bits}")
            return False

        n_frames = len(samples) // n_channels

        # Calcular longitud de cada region de fade en frames
        fi_frames = max(1, min(int(sample_rate * fade_in_ms  / 1000.0), n_frames))
        fo_frames = max(0, min(int(sample_rate * fade_out_ms / 1000.0), n_frames - fi_frames))

        # Fade in coseno: de 0 a 1 en los primeros fi_frames
        if fi_frames > 0:
            env_in = (1.0 - np.cos(np.linspace(0.0, math.pi, fi_frames))) / 2.0
            for ch in range(n_channels):
                samples[ch: fi_frames * n_channels: n_channels] *= env_in

        # Fade out coseno: de 1 a 0 en los ultimos fo_frames
        if fo_frames > 0:
            env_out = (1.0 + np.cos(np.linspace(0.0, math.pi, fo_frames))) / 2.0
            start   = (n_frames - fo_frames) * n_channels
            for ch in range(n_channels):
                samples[start + ch:: n_channels][: fo_frames] *= env_out

        # Convertir de vuelta al formato original del archivo
        if w_format == 3 and bits == 32:
            out_bytes = samples.astype(np.float32).tobytes()
        else:
            out_bytes = (np.clip(samples, -1.0, 1.0) * 32767.0).astype(np.int16).tobytes()

        # Reconstruir el archivo WAV manteniendo todos los chunks (LIST, etc.)
        result = bytes(raw[: data_offset]) + out_bytes + bytes(raw[data_offset + data_size:])
        with open(path, "wb") as f:
            f.write(result)

        logger.info(f"Fade aplicado a {filename}: in={fade_in_ms}ms out={fade_out_ms}ms")
        return True

    except Exception as e:
        logger.error(f"Error en apply_fade_to_wav({filename}): {e}")
        return False
