import base64
import io
import re

from ...base.types import Image, ImageMetadata, has_pil_module
from ._parse_content_template import _load_media


def get_image_dimensions(data_url: str) -> ImageMetadata | None:
    """
    Extract width and height from a base64 encoded image.

    Args:
        data_url: The data URL containing base64 encoded image data or External URL

    Returns:
        Dictionary with width and height, or None if extraction failed
    """
    try:
        if data_url.startswith("http"):
            binary_data = _load_media(data_url)
        else:
            # Extract the base64 data part from the URL
            # Format is: data:[<media type>][;base64],<data>
            pattern = r"data:image/[^;]+;base64,"
            base64_data = re.sub(pattern, "", data_url)

            # Decode the base64 data
            binary_data = base64.b64decode(base64_data)

        # Use PIL to open the image and get dimensions
        if not has_pil_module:  # pragma: no cover
            raise ImportError("PIL module is not available")
        with Image.open(io.BytesIO(binary_data)) as image:
            width, height = image.size

        return ImageMetadata(width=width, height=height)
    except Exception:
        return None
