"""The `Thinking` content class."""

from dataclasses import dataclass
from typing import Literal


@dataclass(kw_only=True)
class Thinking:
    """Thinking content for a message.

    Represents the thinking or thought process of the assistant. This is part
    of an assistant message's content.
    """

    type: Literal["thinking"] = "thinking"

    id: str
    """The ID of the thinking content."""

    thoughts: str
    """The thoughts or reasoning of the assistant."""

    redacted: bool = False
    """Whether the thinking is redacted or not."""


@dataclass(kw_only=True)
class ThinkingChunk:
    """Streaming thinking content chunk."""

    type: Literal["thinking_chunk"] = "thinking_chunk"

    id: str | None = None
    """A unique identifier for this series of chunks, if available."""

    delta: str
    """The incremental thinking text present in this particular chunk."""

    final: bool
    """Whether this is the final piece of content in its sequence. If true, this content's partial is finished generating."""

    def __repr__(self) -> str:
        """Strategic representation for clean default printing."""
        return self.delta
