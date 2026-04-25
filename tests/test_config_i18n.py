"""Pruebas basicas de configuracion e internacionalizacion."""
import os
import tempfile
import unittest

from src.models.config_model import AppConfig
from src.backend.sound_synth import generate_missing_hdd_sounds, get_existing_variant_files
from src.utils.i18n import Translator


class ConfigModelTests(unittest.TestCase):
    """Valida que AppConfig sea retrocompatible y robusto."""

    def test_from_dict_completa_sonidos_faltantes(self):
        # Simula un config antiguo incompleto para validar normalizacion.
        data = {
            "version": "2.0.0",
            "sounds": {
                "read": {"enabled": True, "file": "", "volume": 100}
            },
        }

        config = AppConfig.from_dict(data)

        self.assertIn("read", config.sounds)
        self.assertIn("write", config.sounds)
        self.assertIn("both", config.sounds)
        self.assertEqual(config.sounds["read"].file, "hdd_seek.wav")
        self.assertEqual(config.sounds["write"].file, "hdd_seek.wav")
        self.assertEqual(config.sounds["both"].file, "hdd_spin.wav")

    def test_idioma_invalido_hace_fallback_es(self):
        config = AppConfig(language="xx")
        self.assertEqual(config.language, "es")

    def test_fade_profile_invalido_hace_fallback_balanced(self):
        config = AppConfig(hdd_fade_profile="invalid")
        self.assertEqual(config.hdd_fade_profile, "balanced")


class I18NTests(unittest.TestCase):
    """Valida traducciones y fallback."""

    def test_translator_fallback_and_switch(self):
        translator = Translator("xx")
        self.assertEqual(translator.language, "es")
        self.assertEqual(translator.t("menu.quit"), "Salir")

        translator.set_language("en")
        self.assertEqual(translator.t("menu.quit"), "Quit")


class SyntheticSoundTests(unittest.TestCase):
    """Valida que los sonidos fallback se puedan crear sin samples."""

    def test_generate_missing_hdd_sounds_creates_wav_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            generate_missing_hdd_sounds(temp_dir, variants=3)

            self.assertTrue(os.path.exists(os.path.join(temp_dir, "hdd_seek.wav")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "hdd_click.wav")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "hdd_spin.wav")))

            seek_variants = get_existing_variant_files(temp_dir, "hdd_seek.wav", variants=3)
            self.assertGreaterEqual(len(seek_variants), 3)


if __name__ == "__main__":
    unittest.main()
