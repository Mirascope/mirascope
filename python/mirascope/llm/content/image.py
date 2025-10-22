"""The `Image` content class."""

import base64
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, get_args

import httpx

ImageMimeType = Literal[
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/gif",
    "image/heic",
    "image/heif",
]  # TODO: add e2e tests for every supported type

MIME_TYPES = get_args(ImageMimeType)

# Maximum image size in bytes (20MB)
MAX_IMAGE_SIZE = 20 * 1024 * 1024


def infer_image_type(image_data: bytes) -> ImageMimeType:
    """Get the MIME type of an image from its raw bytes.

    Raises:
        ValueError: If the image type cannot be determined or data is too small
    """
    if len(image_data) < 12:
        raise ValueError("Image data too small to determine type (minimum 12 bytes)")

    if image_data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    elif image_data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    elif image_data.startswith(b"GIF87a") or image_data.startswith(b"GIF89a"):
        return "image/gif"
    elif image_data.startswith(b"RIFF") and image_data[8:12] == b"WEBP":
        return "image/webp"
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
            return "image/heic"
        elif subtype in (b"mif1", b"msf1", b"hevc", b"hevx"):
            return "image/heif"
    raise ValueError("Unsupported image type")


@dataclass(kw_only=True)
class Base64ImageSource:
    """Image data represented as a base64 encoded string."""

    type: Literal["base64_image_source"]

    data: str
    """The image data, as a base64 encoded string."""

    mime_type: ImageMimeType
    """The mime type of the image (e.g. image/png)."""


def _process_image_bytes(data: bytes, max_size: int) -> Base64ImageSource:
    """Validate and process image bytes into a Base64ImageSource.

    Args:
        data: Raw image bytes
        max_size: Maximum allowed size in bytes

    Returns:
        A Base64ImageSource with validated and encoded data

    Raises:
        ValueError: If data size exceeds max_size
    """
    size = len(data)
    if size > max_size:
        raise ValueError(
            f"Image size ({size} bytes) exceeds maximum allowed size ({max_size} bytes)"
        )

    mime_type = infer_image_type(data)
    encoded_data = base64.b64encode(data).decode("utf-8")
    return Base64ImageSource(
        type="base64_image_source",
        data=encoded_data,
        mime_type=mime_type,
    )


@dataclass(kw_only=True)
class URLImageSource:
    """Image data referenced via external URL."""

    type: Literal["url_image_source"]

    url: str
    """The url of the image (e.g. https://example.com/sazed.png)."""


@dataclass(kw_only=True)
class Image:
    """Image content for a message.

    Images can be included in messages to provide visual context. This can be
    used for both input (e.g., user uploading an image) and output (e.g., model
    generating an image).
    """

    type: Literal["image"] = "image"

    source: Base64ImageSource | URLImageSource

    @classmethod
    def from_url(cls, url: str) -> "Image":
        """Create an `Image` reference from a URL, without downloading it.

        Args:
            url: The URL of the image

        Returns:
            An `Image` with a `URLImageSource`
        """
        return cls(source=URLImageSource(type="url_image_source", url=url))

    @classmethod
    def download(cls, url: str, *, max_size: int = MAX_IMAGE_SIZE) -> "Image":
        """Download and encode an image from a URL.

        Args:
            url: The URL of the image to download
            max_size: Maximum allowed image size in bytes (default: 20MB)

        Returns:
            An `Image` with a `Base64ImageSource`

        Raises:
            ValueError: If the downloaded image exceeds max_size
        """
        response = httpx.get(url, follow_redirects=True)
        response.raise_for_status()
        return cls(source=_process_image_bytes(response.content, max_size))

    @classmethod
    async def download_async(
        cls, url: str, *, max_size: int = MAX_IMAGE_SIZE
    ) -> "Image":
        """Asynchronously download and encode an image from a URL.

        Args:
            url: The URL of the image to download
            max_size: Maximum allowed image size in bytes (default: 20MB)

        Returns:
            An `Image` with a `Base64ImageSource`

        Raises:
            ValueError: If the downloaded image exceeds max_size
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            return cls(source=_process_image_bytes(response.content, max_size))

    @classmethod
    def from_file(cls, file_path: str, *, max_size: int = MAX_IMAGE_SIZE) -> "Image":
        """Create an `Image` from a file path.

        Args:
            file_path: Path to the image file
            max_size: Maximum allowed image size in bytes (default: 20MB)

        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file size exceeds max_size
        """
        path = Path(file_path)
        file_size = path.stat().st_size
        if file_size > max_size:
            raise ValueError(
                f"Image file size ({file_size} bytes) exceeds maximum allowed size ({max_size} bytes)"
            )
        with open(path, "rb") as f:
            image_bytes = f.read()
        return cls(source=_process_image_bytes(image_bytes, max_size))

    @classmethod
    def from_bytes(cls, data: bytes, *, max_size: int = MAX_IMAGE_SIZE) -> "Image":
        """Create an `Image` from raw bytes.

        Args:
            data: Raw image bytes
            max_size: Maximum allowed image size in bytes (default: 20MB)

        Raises:
            ValueError: If the data size exceeds max_size
        """
        return cls(source=_process_image_bytes(data, max_size))
