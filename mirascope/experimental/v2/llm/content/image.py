"""The `Image` content class."""

from dataclasses import dataclass
from typing import Literal


@dataclass(kw_only=True)
class Image:
    """Image content for a message.

    Images can be included in messages to provide visual context. This can be
    used for both input (e.g., user uploading an image) and output (e.g., model
    generating an image).
    """

    type: Literal["image"] = "image"

    id: str | None
    """A unique identifier for this image content. This is useful for tracking and referencing generated images."""

    data: str | bytes
    """The image data, which can be a URL, file path, base64-encoded string, or binary data."""

    mime_type: Literal[
        "image/png",
        "image/jpeg",
        "image/webp",
        "image/gif",
        "image/heic",
        "image/heif",
    ]
    """The MIME type of the image, e.g., 'image/png', 'image/jpeg'."""
