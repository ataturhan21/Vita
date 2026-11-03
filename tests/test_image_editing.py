"""Offline checks for upload normalization and the remove.bg key lookup."""

import importlib.util
import unittest
from pathlib import Path

from PIL import Image, ImageEnhance

spec = importlib.util.spec_from_file_location(
    "image_ops", Path(__file__).parents[1] / "vita/modules/image_ops.py"
)
image_ops = importlib.util.module_from_spec(spec)
spec.loader.exec_module(image_ops)


def run_enhancers(image):
    for enhancer in (
        ImageEnhance.Sharpness,
        ImageEnhance.Color,
        ImageEnhance.Brightness,
        ImageEnhance.Contrast,
    ):
        image = enhancer(image).enhance(1.0)
    return image


class EditableImageTests(unittest.TestCase):
    def test_modes_rejected_by_enhancers_are_converted(self):
        for mode in ("P", "1", "I;16", "I", "F"):
            with self.subTest(mode=mode):
                image = image_ops.editable_image(Image.new(mode, (4, 4)))
                self.assertEqual(image.mode, "RGB")
                run_enhancers(image)

    def test_palette_transparency_becomes_alpha(self):
        source = Image.new("P", (2, 2))
        source.info["transparency"] = 0
        image = image_ops.editable_image(source)
        self.assertEqual(image.mode, "RGBA")
        self.assertEqual(image.getpixel((0, 0))[3], 0)
        run_enhancers(image)

    def test_supported_modes_are_unchanged(self):
        for mode in ("RGB", "RGBA", "L", "LA", "CMYK"):
            with self.subTest(mode=mode):
                source = Image.new(mode, (2, 2))
                self.assertIs(image_ops.editable_image(source), source)


class MissingSecrets(dict):
    def load_if_toml_exists(self):
        return False

    def __getitem__(self, key):
        raise AssertionError("secrets must not be read without a file")


class RemoveBgKeyTests(unittest.TestCase):
    def test_configured_key_is_returned(self):
        self.assertEqual(
            image_ops.removebg_api_key({"removebg_api_key": "key"}), "key"
        )

    def test_missing_or_empty_key_returns_none(self):
        self.assertIsNone(image_ops.removebg_api_key({}))
        self.assertIsNone(image_ops.removebg_api_key({"removebg_api_key": ""}))

    def test_missing_secrets_file_returns_none(self):
        self.assertIsNone(image_ops.removebg_api_key(MissingSecrets()))


if __name__ == "__main__":
    unittest.main()
