"""The `TextChunk` content class."""

from dataclasses import dataclass
from typing import Literal


@dataclass(kw_only=True)
class TextChunk:
    """Streaming text content chunk."""

    type: Literal["text_chunk"] = "text_chunk"

    id: str | None = None
    """A unique identifier for this series of chunks, if available."""

    delta: str
    """The incremental text present in this particular chunk."""

    def __repr__(self) -> str:
        """Strategic representation for clean default printing."""
        return self.delta
