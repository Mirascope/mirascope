"""The `Text` content class."""

from dataclasses import dataclass
from typing import Literal


@dataclass(kw_only=True)
class Text:
    """Text content for a message."""

    type: Literal["text"] = "text"

    text: str
    """The text content."""


@dataclass(kw_only=True)
class TextStartChunk:
    """Represents the start of a text chunk stream."""

    type: Literal["text_start_chunk"] = "text_start_chunk"

    content_type: Literal["text"] = "text"
    """The type of content reconstructed by this chunk."""


@dataclass(kw_only=True)
class TextChunk:
    """Represents an incremental text chunk in a stream."""

    type: Literal["text_chunk"] = "text_chunk"

    content_type: Literal["text"] = "text"
    """The type of content reconstructed by this chunk."""

    delta: str
    """The incremental text added in this chunk."""


@dataclass(kw_only=True)
class TextEndChunk:
    """Represents the end of a text chunk stream."""

    type: Literal["text_end_chunk"] = "text_end_chunk"

    content_type: Literal["text"] = "text"
    """The type of content reconstructed by this chunk."""
