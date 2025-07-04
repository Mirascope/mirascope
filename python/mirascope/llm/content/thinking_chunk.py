"""The `ThinkingChunk` content class."""

from dataclasses import dataclass
from typing import Literal


@dataclass(kw_only=True)
class ThinkingChunk:
    """Streaming thinking content chunk."""

    type: Literal["thinking_chunk"] = "thinking_chunk"

    id: str | None = None
    """A unique identifier for this series of chunks, if available."""

    delta: str
    """The incremental thinking text present in this particular chunk."""

    partial: str
    """The accumulated thinking text in this series of chunks."""