import importlib.util
import unittest
from io import BytesIO
from pathlib import Path

from PIL import Image

spec = importlib.util.spec_from_file_location(
    "image_ops", Path(__file__).parents[1] / "vita/modules/image_ops.py"
)
image_ops = importlib.util.module_from_spec(spec)
spec.loader.exec_module(image_ops)


class ImageOperationTests(unittest.TestCase):
    def test_rgba_inversion_preserves_alpha(self):
        source = Image.new("RGBA", (2, 1), (10, 20, 30, 40))
        result = image_ops.invert_image(source)
        self.assertEqual(result.getpixel((0, 0)), (245, 235, 225, 40))
        self.assertEqual(source.getpixel((0, 0)), (10, 20, 30, 40))

    def test_grayscale_alpha_is_preserved(self):
        result = image_ops.invert_image(Image.new("LA", (1, 1), (10, 40)))
        self.assertEqual(result.getpixel((0, 0)), (245, 40))

    def test_export_is_a_real_png(self):
        source = Image.new("RGBA", (2, 3), (1, 2, 3, 4))
        with Image.open(BytesIO(image_ops.png_bytes(source))) as result:
            self.assertEqual(result.format, "PNG")
            self.assertEqual(result.size, source.size)
            self.assertEqual(result.getpixel((0, 0)), (1, 2, 3, 4))

    def test_cmyk_export_is_converted_to_rgb(self):
        source = Image.new("CMYK", (2, 3), (0, 128, 255, 0))
        with Image.open(BytesIO(image_ops.png_bytes(source))) as result:
            self.assertEqual(result.mode, "RGB")
            self.assertEqual(
                result.getpixel((0, 0)), source.convert("RGB").getpixel((0, 0))
            )

    def test_background_removal_uses_unique_cleaned_directories(self):
        paths = []

        class FakeClient:
            def __init__(self, key, log_path):
                pass

            def remove_background_from_img_file(
                self, img_file_path, new_file_name
            ):
                paths.append(Path(img_file_path))
                with Image.open(img_file_path) as source:
                    source.save(new_file_name)

        sources = [
            Image.new("RGBA", (1, 1), (1, 2, 3, 4)),
            Image.new("CMYK", (1, 1), (0, 0, 0, 0)),
        ]
        for source in sources:
            result = image_ops.remove_background(source, "test", FakeClient)
            self.assertEqual(
                result.getpixel((0, 0)),
                source.convert("RGB").getpixel((0, 0))
                if source.mode == "CMYK"
                else source.getpixel((0, 0)),
            )
        self.assertNotEqual(paths[0].parent, paths[1].parent)
        self.assertTrue(all(not path.parent.exists() for path in paths))

    def test_failed_service_cleans_workspace(self):
        paths = []

        class FakeClient:
            def __init__(self, key, log_path):
                pass

            def remove_background_from_img_file(
                self, img_file_path, new_file_name
            ):
                paths.append(Path(img_file_path))

        with self.assertRaisesRegex(RuntimeError, "did not produce"):
            image_ops.remove_background(
                Image.new("RGB", (1, 1)), "test", FakeClient
            )
        self.assertFalse(paths[0].parent.exists())


if __name__ == "__main__":
    unittest.main()
