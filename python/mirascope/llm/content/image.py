"""The `Image` content class."""

from dataclasses import dataclass
from typing import Literal

ImageMimeType = Literal[
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/gif",
    "image/heic",
    "image/heif",
]


@dataclass(kw_only=True)
class Base64ImageSource:
    """Image data represented as a base64 encoded string."""

    type: Literal["base64_image_source"]

    data: str
    """The image data, as a base64 encoded string."""

    mime_type: ImageMimeType
    """The mime type of the image (e.g. image/png)."""


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
    def from_url(
        cls,
        url: str,
        *,
        download: bool = False,
    ) -> "Image":
        """Create an `Image` from a URL."""
        raise NotImplementedError

    @classmethod
    def from_file(
        cls,
        file_path: str,
        *,
        mime_type: ImageMimeType | None,
    ) -> "Image":
        """Create an `Image` from a file path."""
        raise NotImplementedError

    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        *,
        mime_type: ImageMimeType | None,
    ) -> "Image":
        """Create an `Image` from raw bytes."""
        raise NotImplementedError
