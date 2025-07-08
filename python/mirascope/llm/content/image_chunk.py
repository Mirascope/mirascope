"""The `ImageChunk` content class."""

from dataclasses import dataclass
from typing import Literal

from .image import ImageMimeType


@dataclass(kw_only=True)
class ImageChunk:
    """Image content chunk when streaming.

    Contains progressive image data as it's being generated.
    """

    type: Literal["image_chunk"] = "image_chunk"

    mime_type: ImageMimeType
    """The MIME type of the image, e.g., 'image/png', 'image/jpeg'."""

    id: str | None = None
    """A unique identifier for this image content. This is useful for tracking and referencing generated images."""

    delta: str
    """The progressive image data for this rendering stage as a base64 encoded string."""

    def __repr__(self) -> str:
        """Strategic representation for clean default printing."""
        return "."
