"""The `Text` content class."""

from dataclasses import dataclass
from typing import Literal


@dataclass(kw_only=True)
class Text:
    """Text content for a message."""

    type: Literal["text"] = "text"

    text: str


@dataclass(kw_only=True)
class TextChunk:
    """Partially reconstructed text content from chunk stream.

    Contains both the accumulated text and the current delta for this update.
    """

    type: Literal["text_chunk"] = "text_chunk"

    text: str
    """The accumulated text content from all received chunks."""

    delta: str
    """The incremental text added in the most recent chunk."""
