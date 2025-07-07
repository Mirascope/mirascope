"""The `ImageChunk` content class."""

from dataclasses import dataclass
from typing import Literal


@dataclass(kw_only=True)
class ImagePartial:
    """Image content chunk when streaming.

    The partial field contains bytes data of the current state of the image, which
    may be progressively rendering. There is no delta.
    """

    type: Literal["image_partial"] = "image_partial"

    mime_type: Literal[
        "image/png",
        "image/jpeg",
        "image/webp",
        "image/gif",
        "image/heic",
        "image/heif",
    ]
    """The MIME type of the image, e.g., 'image/png', 'image/jpeg'."""

    id: str | None = None
    """A unique identifier for this image content. This is useful for tracking and referencing generated images."""

    partial: str
    """The progressive image data for this rendering stage as a base64 encoded string."""
