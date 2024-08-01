"""Tests the `_utils.get_image_type` module."""

import pytest

from mirascope.core.base._utils._get_image_type import get_image_type

JPEG_DATA = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x02\x01\x00e\x00e\x00\x00\xff\xe1\x10>Exif\x00\x00"

PNG_DATA = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x03 \x00\x00\x02X\x08\x06\x00\x00\x00\x9a"

GIF_DATA = b"GIF89a\x90\x01\x90\x01\xf7\x00\x00\x00\x00\x00\x00\x009\x00\x00A\x00\x001\x00\x00\x08\x00\x00"

WEBP_DATA = b"RIFFhv\x00\x00WEBPVP8 \\v\x00\x00\xd2\xbe\x01\x9d\x01*&\x02p\x01"

HEIC_DATA = b"\x00\x00\x00\x18ftypheic\x00\x00\x00\x00mif1heic\x00\x00\x01\xb7me"

HEIF_DATA = b"\x00\x00\x00\x18ftyphevx\x00\x00\x00\x00mif1heic\x00\x00\x01\xb7me"


def test_get_image_type() -> None:
    """Test the get_image_type function."""
    assert get_image_type(JPEG_DATA) == "jpeg"
    assert get_image_type(PNG_DATA) == "png"
    assert get_image_type(GIF_DATA) == "gif"
    assert get_image_type(WEBP_DATA) == "webp"
    assert get_image_type(HEIC_DATA) == "heic"
    assert get_image_type(HEIF_DATA) == "heif"
    with pytest.raises(ValueError, match="Unsupported image type"):
        get_image_type(b"invalid")
