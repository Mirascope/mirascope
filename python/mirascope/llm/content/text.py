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
    """Streaming text content chunk."""

    type: Literal["text_chunk"] = "text_chunk"

    delta: str
    """The incremental text present in this particular chunk."""

    final: bool
    """Whether this is the final piece of content in its sequence. If true, this content's partial is finished generating."""

    def __repr__(self) -> str:
        """Strategic representation for clean default printing."""
        return self.delta
