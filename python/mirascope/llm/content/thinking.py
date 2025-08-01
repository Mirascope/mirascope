"""The `Thinking` content class."""

from dataclasses import dataclass
from typing import Literal


@dataclass(kw_only=True)
class Thinking:
    """Thinking content for a message.

    Represents the thinking or thought process of the assistant.
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
    """A chunk of Thinking content.

    Contains both the accumulated thoughts and the current delta for this update.
    """

    type: Literal["thinking_chunk"] = "thinking_chunk"

    id: str
    """The id of the thinking content."""

    thoughts: str
    """The accumulated thoughts or reasoning from all received chunks."""

    delta: str
    """The incremental thinking text added in this update.
    
    May be an empty string if the most recent chunk was providing the signature rather
    than thinking content."""

    redacted: bool = False
    """Whether the thinking is redacted or not."""
