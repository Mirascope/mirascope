from io import BytesIO

from ..types import Image


def pil_image_to_bytes(image: Image.Image) -> bytes:
    try:
        image_bytes = BytesIO()
        image.save(image_bytes, format=image.format if image.format else None)
        image_bytes.seek(0)
        return image_bytes.read()
    except Exception as e:
        raise ValueError(f"Error converting image to bytes: {e}") from e
