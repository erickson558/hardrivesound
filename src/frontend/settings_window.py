"""
Panel GUI de configuracion para Hard Drive Sound Simulator.
Se abre desde el menu de bandeja sin bloquear el monitor de disco.

Secciones:
  1. Core         — habilitar global, delay, idioma, comportamiento de icono
  2. Archivos     — selector de WAV para lectura y escritura
  3. Fade         — sliders de fade-in y fade-out (ms) para archivos reales
  4. Triggers     — en que eventos se dispara el sonido
  5. Botones      — Aplicar / Donar / Cerrar
"""
import os
import re
import threading
import tkinter as tk
from tkinter import ttk
from typing import List, Optional

from src.backend.config_manager import ConfigManager
from src.backend.disk_monitor import DiskMonitor
from src.backend.sound_synth import apply_fade_to_wav, generate_missing_hdd_sounds
from src.frontend.tray_interface import TrayInterface
from src.utils.constants import AVAILABLE_DELAYS, ICON_BEHAVIORS
from src.utils.i18n import Translator
from src.utils.logger import logger


# ── Utilidad de exploracion de archivos ─────────────────────────────────────

def _list_wav_files(base_dir: str) -> List[str]:
    """
    Lista los archivos .wav disponibles en base_dir.
    Excluye variantes sinteticas con patron _v<numero>.wav (ej. hdd_seek_v1.wav).
    """
    try:
        variant_pattern = re.compile(r"_v\d+\.wav$", re.IGNORECASE)
        files = [
            f for f in os.listdir(base_dir)
            if f.lower().endswith(".wav") and not variant_pattern.search(f.lower())
        ]
        return sorted(files)
    except Exception:
        # Fallback con archivos conocidos si el directorio no es accesible
        return ["hdd_seek.wav", "hdd_click.wav", "hdd_spin.wav"]


# ── Ventana principal ────────────────────────────────────────────────────────

class SettingsWindow:
    """
    Ventana de configuracion basada en tkinter.

    Permite seleccionar archivos WAV para lectura/escritura, ajustar
    fade in/out con sliders, y persistir todo en config.json.
    """

    def __init__(
        self,
        config_manager: ConfigManager,
        disk_monitor: DiskMonitor,
        tray_interface: TrayInterface,
    ) -> None:
        self.config_manager = config_manager
        self.disk_monitor   = disk_monitor
        self.tray_interface = tray_interface

        # Lock para evitar abrir multiples ventanas en paralelo
        self._window_lock = threading.Lock()
        self._is_open     = False
        self._root: Optional[tk.Tk] = None

    # ── Apertura ─────────────────────────────────────────────────────────────

    def open_window(self) -> None:
        """Abrir la ventana en un hilo dedicado para no bloquear el tray."""
        with self._window_lock:
            if self._is_open:
                logger.info("El panel de configuracion ya esta abierto")
                return
            self._is_open = True

        # Hilo daemon para que la ventana no bloquee el cierre de la app
        threading.Thread(target=self._run_window, daemon=True).start()

    # ── Construccion de la GUI ───────────────────────────────────────────────

    def _run_window(self) -> None:
        """Construir y ejecutar la ventana tkinter en su propio hilo."""
        config     = self.config_manager.config
        base_dir   = self.config_manager.base_dir
        translator = Translator(config.language)

        root = tk.Tk()
        self._root = root
        root.title(translator.t("gui.title"))
        root.geometry("660x810")
        root.resizable(False, False)

        # ── Estilos visuales (tema oscuro) ────────────────────────────────
        style = ttk.Style(root)
        style.theme_use("clam")
        root.configure(bg="#0f141a")
        style.configure("Panel.TFrame",           background="#0f141a")
        style.configure("Card.TFrame",            background="#17202b")
        style.configure("Card.TLabelframe",       background="#17202b",
                         foreground="#f6f7f9", borderwidth=1)
        style.configure("Card.TLabelframe.Label", background="#17202b",
                         foreground="#9bd2ff", font=("Segoe UI", 10, "bold"))
        style.configure("Panel.TLabel",           background="#0f141a",
                         foreground="#e4e9ef", font=("Segoe UI", 10))
        style.configure("Card.TLabel",            background="#17202b",
                         foreground="#e4e9ef", font=("Segoe UI", 10))
        style.configure("Val.TLabel",             background="#17202b",
                         foreground="#9bd2ff",  font=("Segoe UI", 10, "bold"))
        style.configure("Title.TLabel",           background="#0f141a",
                         foreground="#ffffff",  font=("Segoe UI", 16, "bold"))
        style.configure("Subtitle.TLabel",        background="#0f141a",
                         foreground="#8fa6bf",  font=("Segoe UI", 9))
        style.configure("Accent.TButton",         font=("Segoe UI", 10, "bold"))

        # ── Cierre de ventana ─────────────────────────────────────────────
        def _close_window() -> None:
            """Destruir la ventana y liberar el lock para permitir reabrir."""
            try:
                root.destroy()
            finally:
                with self._window_lock:
                    self._is_open = False
                self._root = None

        root.protocol("WM_DELETE_WINDOW", _close_window)

        # ── Contenedor principal ──────────────────────────────────────────
        container = ttk.Frame(root, padding=18, style="Panel.TFrame")
        container.pack(fill="both", expand=True)

        # ── Encabezado ────────────────────────────────────────────────────
        title_label    = ttk.Label(container, text=translator.t("gui.title"),
                                    style="Title.TLabel")
        subtitle_label = ttk.Label(container, text="Hard Drive Vintage Tuning",
                                    style="Subtitle.TLabel")
        title_label.pack(anchor="w")
        subtitle_label.pack(anchor="w", pady=(0, 12))

        # ── Variables de control ligadas a widgets ────────────────────────
        global_sound_var  = tk.BooleanVar(value=config.enabled)
        delay_var         = tk.StringVar(value=str(config.global_delay))
        language_var      = tk.StringVar(value=config.language)
        behavior_var      = tk.StringVar(value=config.icon_behavior)

        # Fade in/out: recuperar de config con valores por defecto seguros
        fade_in_var  = tk.DoubleVar(value=getattr(config, "fade_in_ms",  20.0))
        fade_out_var = tk.DoubleVar(value=getattr(config, "fade_out_ms", 40.0))

        # Disparadores de actividad de disco
        trigger_read_var  = tk.BooleanVar(value=config.sound_triggers.read)
        trigger_write_var = tk.BooleanVar(value=config.sound_triggers.write)
        trigger_both_var  = tk.BooleanVar(value=config.sound_triggers.both)

        # Habilitacion de cada tipo de sonido
        sound_read_var  = tk.BooleanVar(value=config.sounds["read"].enabled)
        sound_write_var = tk.BooleanVar(value=config.sounds["write"].enabled)
        sound_both_var  = tk.BooleanVar(value=config.sounds["both"].enabled)

        # Archivos WAV disponibles en la carpeta de la aplicacion
        available_wavs = _list_wav_files(base_dir) or ["hdd_seek.wav"]

        # Archivo actualmente asignado a lectura y escritura
        sound_read_file_var  = tk.StringVar(
            value=config.sounds["read"].file  or "hdd_seek.wav")
        sound_write_file_var = tk.StringVar(
            value=config.sounds["write"].file or "hdd_seek.wav")

        # ── SECCION 1: Core ───────────────────────────────────────────────
        top_card = ttk.LabelFrame(container, text="Core",
                                   padding=10, style="Card.TLabelframe")
        top_card.pack(fill="x", pady=(0, 8))

        # Activacion global del simulador de sonido
        global_sound_check = ttk.Checkbutton(
            top_card, text=translator.t("gui.global_sound"),
            variable=global_sound_var)
        global_sound_check.pack(anchor="w", pady=(0, 6))

        # Selector de delay entre disparos consecutivos
        delay_label = ttk.Label(top_card, text=translator.t("gui.delay"),
                                 style="Panel.TLabel")
        delay_label.pack(anchor="w")
        delay_combo = ttk.Combobox(
            top_card, textvariable=delay_var, state="readonly",
            values=[str(v) for v in AVAILABLE_DELAYS])
        delay_combo.pack(fill="x", pady=(0, 6))

        # Selector de idioma (cambia textos en tiempo real al seleccionar)
        language_label = ttk.Label(top_card, text=translator.t("gui.language"),
                                    style="Panel.TLabel")
        language_label.pack(anchor="w")
        language_combo = ttk.Combobox(
            top_card, textvariable=language_var, state="readonly",
            values=["es", "en"])
        language_combo.pack(fill="x", pady=(0, 6))

        # Comportamiento del icono de bandeja ante actividad de disco
        behavior_label = ttk.Label(
            top_card, text=translator.t("gui.icon_behavior"),
            style="Panel.TLabel")
        behavior_label.pack(anchor="w")
        behavior_combo = ttk.Combobox(
            top_card, textvariable=behavior_var, state="readonly",
            values=ICON_BEHAVIORS)
        behavior_combo.pack(fill="x", pady=(0, 2))

        # ── SECCION 2: Archivos de Sonido ─────────────────────────────────
        sound_card = ttk.LabelFrame(
            container, text=translator.t("gui.sound_files"),
            padding=10, style="Card.TLabelframe")
        sound_card.pack(fill="x", pady=(0, 8))

        # --- Fila Lectura: checkbox de habilitacion + selector de archivo ---
        read_row = ttk.Frame(sound_card, style="Card.TFrame")
        read_row.pack(fill="x", pady=(0, 6))
        sound_read_check = ttk.Checkbutton(
            read_row, text="", variable=sound_read_var, width=2)
        sound_read_check.pack(side="left")
        sound_read_label = ttk.Label(
            read_row, text=translator.t("gui.sound_read_file"),
            style="Card.TLabel", width=13)
        sound_read_label.pack(side="left", padx=(0, 4))
        sound_read_combo = ttk.Combobox(
            read_row, textvariable=sound_read_file_var,
            state="readonly", values=available_wavs)
        sound_read_combo.pack(side="left", fill="x", expand=True)

        # --- Fila Escritura: checkbox de habilitacion + selector de archivo ---
        write_row = ttk.Frame(sound_card, style="Card.TFrame")
        write_row.pack(fill="x", pady=(0, 6))
        sound_write_check = ttk.Checkbutton(
            write_row, text="", variable=sound_write_var, width=2)
        sound_write_check.pack(side="left")
        sound_write_label = ttk.Label(
            write_row, text=translator.t("gui.sound_write_file"),
            style="Card.TLabel", width=13)
        sound_write_label.pack(side="left", padx=(0, 4))
        sound_write_combo = ttk.Combobox(
            write_row, textvariable=sound_write_file_var,
            state="readonly", values=available_wavs)
        sound_write_combo.pack(side="left", fill="x", expand=True)

        # --- Fila Ambos: solo checkbox (usa el WAV de lectura internamente) ---
        sound_both_check = ttk.Checkbutton(
            sound_card, text=translator.t("gui.both"), variable=sound_both_var)
        sound_both_check.pack(anchor="w")

        # ── SECCION 3: Fade In / Fade Out ──────────────────────────────────
        fade_card = ttk.LabelFrame(
            container, text=translator.t("gui.fade_adjust"),
            padding=10, style="Card.TLabelframe")
        fade_card.pack(fill="x", pady=(0, 8))

        # --- Fade In (0–200 ms) ---
        fi_row = ttk.Frame(fade_card, style="Card.TFrame")
        fi_row.pack(fill="x", pady=(0, 6))
        fade_in_label = ttk.Label(
            fi_row, text=translator.t("gui.fade_in"),
            style="Card.TLabel", width=14)
        fade_in_label.pack(side="left")
        fade_in_scale = ttk.Scale(
            fi_row, from_=0, to=200, orient="horizontal", variable=fade_in_var)
        fade_in_scale.pack(side="left", fill="x", expand=True, padx=(4, 8))
        # Etiqueta que muestra el valor en ms junto al slider
        fade_in_val_label = ttk.Label(
            fi_row, text=f"{int(fade_in_var.get())} ms",
            style="Val.TLabel", width=8)
        fade_in_val_label.pack(side="left")

        # --- Fade Out (0–500 ms) ---
        fo_row = ttk.Frame(fade_card, style="Card.TFrame")
        fo_row.pack(fill="x")
        fade_out_label = ttk.Label(
            fo_row, text=translator.t("gui.fade_out"),
            style="Card.TLabel", width=14)
        fade_out_label.pack(side="left")
        fade_out_scale = ttk.Scale(
            fo_row, from_=0, to=500, orient="horizontal", variable=fade_out_var)
        fade_out_scale.pack(side="left", fill="x", expand=True, padx=(4, 8))
        fade_out_val_label = ttk.Label(
            fo_row, text=f"{int(fade_out_var.get())} ms",
            style="Val.TLabel", width=8)
        fade_out_val_label.pack(side="left")

        # Callback que actualiza las etiquetas de valor mientras se arrastra
        def _update_fade_labels(*_args) -> None:
            """Refrescar el texto de ms junto a cada slider al moverlo."""
            fade_in_val_label.configure(text=f"{int(fade_in_var.get())} ms")
            fade_out_val_label.configure(text=f"{int(fade_out_var.get())} ms")

        fade_in_var.trace_add("write",  _update_fade_labels)
        fade_out_var.trace_add("write", _update_fade_labels)

        # ── SECCION 4: Triggers de actividad ──────────────────────────────
        trigger_group = ttk.LabelFrame(
            container, text=translator.t("gui.triggers"),
            padding=10, style="Card.TLabelframe")
        trigger_group.pack(fill="x", pady=(0, 8))
        trigger_read_check  = ttk.Checkbutton(
            trigger_group, text=translator.t("gui.read"),
            variable=trigger_read_var)
        trigger_write_check = ttk.Checkbutton(
            trigger_group, text=translator.t("gui.write"),
            variable=trigger_write_var)
        trigger_both_check  = ttk.Checkbutton(
            trigger_group, text=translator.t("gui.both"),
            variable=trigger_both_var)
        trigger_read_check.pack(anchor="w")
        trigger_write_check.pack(anchor="w")
        trigger_both_check.pack(anchor="w")

        # ── Estado y botones ──────────────────────────────────────────────
        status_var = tk.StringVar(value="")
        status_label = ttk.Label(container, textvariable=status_var,
                                  style="Panel.TLabel")
        status_label.pack(fill="x", pady=(8, 4))

        buttons_frame = ttk.Frame(container, style="Panel.TFrame")
        buttons_frame.pack(fill="x")

        apply_button  = ttk.Button(
            buttons_frame, text=translator.t("gui.apply"),
            command=lambda: _apply_changes(), style="Accent.TButton")
        donate_button = ttk.Button(
            buttons_frame, text=translator.t("gui.donate"),
            command=self.tray_interface.open_donation_link)
        close_button  = ttk.Button(
            buttons_frame, text=translator.t("gui.close"),
            command=_close_window)

        apply_button.pack(side="left",  padx=(0, 8))
        donate_button.pack(side="left", padx=(0, 8))
        close_button.pack(side="right")

        # ── Callbacks internos ────────────────────────────────────────────

        def _refresh_language(new_language: str) -> None:
            """Actualizar TODOS los textos de la ventana al cambiar idioma."""
            translator.set_language(new_language)
            root.title(translator.t("gui.title"))
            title_label.configure(text=translator.t("gui.title"))
            global_sound_check.configure(text=translator.t("gui.global_sound"))
            delay_label.configure(text=translator.t("gui.delay"))
            language_label.configure(text=translator.t("gui.language"))
            behavior_label.configure(text=translator.t("gui.icon_behavior"))
            sound_card.configure(text=translator.t("gui.sound_files"))
            sound_read_label.configure(text=translator.t("gui.sound_read_file"))
            sound_write_label.configure(text=translator.t("gui.sound_write_file"))
            sound_both_check.configure(text=translator.t("gui.both"))
            fade_card.configure(text=translator.t("gui.fade_adjust"))
            fade_in_label.configure(text=translator.t("gui.fade_in"))
            fade_out_label.configure(text=translator.t("gui.fade_out"))
            trigger_group.configure(text=translator.t("gui.triggers"))
            trigger_read_check.configure(text=translator.t("gui.read"))
            trigger_write_check.configure(text=translator.t("gui.write"))
            trigger_both_check.configure(text=translator.t("gui.both"))
            apply_button.configure(text=translator.t("gui.apply"))
            donate_button.configure(text=translator.t("gui.donate"))
            close_button.configure(text=translator.t("gui.close"))

        def _apply_changes() -> None:
            """
            Persistir cambios en config.json y aplicar efectos de audio:

            1. Actualiza el modelo de config desde los controles.
            2. Asigna los archivos WAV seleccionados para lectura y escritura.
            3. Aplica fade in/out a archivos reales (con .bak o tamano > 50 KB).
               Los archivos sinteticos pequenos ya tienen fade incorporado.
            4. Regenera sonidos sinteticos faltantes.
            5. Guarda config.json en el mismo directorio del .exe / .py.
            6. Propaga cambios a los demas componentes de la aplicacion.
            """
            # 1. Leer valores de todos los controles
            config.enabled       = global_sound_var.get()
            config.global_delay  = float(delay_var.get())
            config.language      = language_var.get()
            config.icon_behavior = behavior_var.get()
            config.fade_in_ms    = round(fade_in_var.get(),  1)
            config.fade_out_ms   = round(fade_out_var.get(), 1)

            config.sound_triggers.read  = trigger_read_var.get()
            config.sound_triggers.write = trigger_write_var.get()
            config.sound_triggers.both  = trigger_both_var.get()

            # 2. Actualizar archivos y estado de habilitacion por tipo
            config.sounds["read"].file     = sound_read_file_var.get()
            config.sounds["read"].enabled  = sound_read_var.get()
            config.sounds["write"].file    = sound_write_file_var.get()
            config.sounds["write"].enabled = sound_write_var.get()
            config.sounds["both"].enabled  = sound_both_var.get()

            # 3. Marcar disponibilidad real (verifica existencia en disco)
            for stype in ("read", "write", "both"):
                sc = config.sounds[stype]
                sc.available = os.path.exists(os.path.join(base_dir, sc.file))

            # 4. Aplicar fade a archivos reales (grabaciones externas)
            #    Criterio: tiene .bak (ya procesado antes) o tamano > 50 KB
            for stype in ("read", "write"):
                sc    = config.sounds[stype]
                fpath = os.path.join(base_dir, sc.file)
                bak   = fpath + ".bak"
                if not sc.available:
                    continue
                try:
                    is_real = os.path.exists(bak) or os.path.getsize(fpath) > 50_000
                except OSError:
                    is_real = False
                if is_real:
                    apply_fade_to_wav(
                        base_dir, sc.file,
                        config.fade_in_ms, config.fade_out_ms)

            # 5. Asegurar que los sonidos sinteticos de respaldo existen
            generate_missing_hdd_sounds(base_dir, variants=8)

            # 6. Guardar en config.json (misma carpeta del .exe o .py)
            self.config_manager.save_config()

            # 7. Propagar cambios a la bandeja y al monitor
            self.disk_monitor.set_icon_behavior(config.icon_behavior)
            self.tray_interface.set_language(config.language)
            self.tray_interface.schedule_menu_update()
            self.tray_interface.process_pending_updates()

            status_var.set(translator.t("gui.saved"))
            logger.info("Configuracion aplicada desde panel GUI")

        def _language_changed(event=None) -> None:
            """Disparado al cambiar el selector de idioma."""
            _refresh_language(language_var.get())

        language_combo.bind("<<ComboboxSelected>>", _language_changed)

        root.mainloop()
