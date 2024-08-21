"""Utility for determining the type of an image from its bytes."""


def get_image_type(image_data: bytes) -> str:
    if image_data.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    elif image_data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    elif image_data.startswith(b"GIF87a") or image_data.startswith(b"GIF89a"):
        return "gif"
    elif image_data.startswith(b"RIFF") and image_data[8:12] == b"WEBP":
        return "webp"
    elif image_data[4:12] in (
        b"ftypmif1",
        b"ftypmsf1",
        b"ftypheic",
        b"ftypheix",
        b"ftyphevc",
        b"ftyphevx",
    ):
        subtype = image_data[8:12]
        if subtype in (b"heic", b"heix"):
            return "heic"
        elif subtype in (b"mif1", b"msf1", b"hevc", b"hevx"):
            return "heif"
    raise ValueError("Unsupported image type")
