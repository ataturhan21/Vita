"""Image operations with isolated temporary files and alpha preservation."""

import logging
import tempfile
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps


def invert_image(image):
    """Invert visible color channels while preserving transparency."""
    if image.mode == "RGBA" or "transparency" in image.info:
        rgba = image.convert("RGBA")
        inverted = ImageOps.invert(rgba.convert("RGB")).convert("RGBA")
        inverted.putalpha(rgba.getchannel("A"))
        return inverted
    if image.mode == "LA":
        return Image.merge(
            "LA",
            (ImageOps.invert(image.getchannel("L")), image.getchannel("A")),
        )
    return ImageOps.invert(
        image.convert("RGB") if image.mode != "L" else image
    )


def remove_background(image, api_key, client_factory=None):
    """Use a unique PNG workspace, then return an independent in-memory image."""
    if client_factory is None:
        from removebg import RemoveBg

        client_factory = RemoveBg
    with tempfile.TemporaryDirectory(prefix="vita-image-") as directory:
        source = Path(directory) / "input.png"
        source.write_bytes(png_bytes(image))
        log_path = Path(directory) / "error.log"
        existing_handlers = set(logging.getLogger().handlers)
        try:
            client = client_factory(api_key, str(log_path))
            result = Path(directory) / "edited.png"
            client.remove_background_from_img_file(
                img_file_path=str(source), new_file_name=str(result)
            )
            if not result.is_file():
                raise RuntimeError(
                    "Background removal did not produce an image"
                )
            with Image.open(result) as output:
                return output.copy()
        finally:
            # The legacy client can attach a root file handler. Close only the
            # handler for this workspace so Windows can remove the directory.
            for handler in list(logging.getLogger().handlers):
                if handler not in existing_handlers and getattr(
                    handler, "baseFilename", None
                ) == str(log_path):
                    logging.getLogger().removeHandler(handler)
                    handler.close()


def png_bytes(image):
    output = BytesIO()
    if image.mode not in {"1", "L", "LA", "P", "RGB", "RGBA", "I", "I;16"}:
        image = image.convert("RGB")
    image.save(output, format="PNG")
    return output.getvalue()
