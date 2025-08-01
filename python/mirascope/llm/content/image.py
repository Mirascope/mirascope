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
class Image:
    """Image content for a message.

    Images can be included in messages to provide visual context. This can be
    used for both input (e.g., user uploading an image) and output (e.g., model
    generating an image).
    """

    type: Literal["image"] = "image"

    content_type: Literal["image"] = "image"
    """The type of content being represented."""

    id: str | None = None
    """A unique identifier for this image content. This is useful for tracking and referencing generated images."""

    data: str
    """The image data, as a base64 encoded string."""

    mime_type: ImageMimeType
    """The MIME type of the image, e.g., 'image/png', 'image/jpeg'."""

    @classmethod
    def from_file(
        cls,
        file_path: str,
        *,
        mime_type: ImageMimeType | None,
        id: str | None = None,
    ) -> "Image":
        """Create an Image from a file path."""
        raise NotImplementedError

    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        *,
        mime_type: ImageMimeType | None,
        id: str | None = None,
    ) -> "Image":
        """Create an Image from raw bytes."""
        raise NotImplementedError


@dataclass(kw_only=True)
class ImageUrl:
    """Image content for a message, referenced by url.

    Use ImageUrl when you want to provide image content, but have the LLM load it
    via http. This can be specified as input, but LLM generated images will use standard
    Image content.
    """

    type: Literal["image_url"] = "image_url"

    content_type: Literal["image"] = "image"
    """The type of content being represented."""

    url: str
    """The image url."""

    mime_type: ImageMimeType | None
    """The MIME type of the image, e.g., 'image/png', 'image/jpeg'."""
