"""The `Thinking` content class."""

from dataclasses import dataclass
from typing import Literal


@dataclass(kw_only=True)
class Thinking:
    """Thinking content for a message.

    Represents the thinking or thought process of the assistant.
    """

    type: Literal["thinking"] = "thinking"

    content_type: Literal["thinking"] = "thinking"
    """The type of content being represented."""

    signature: str | None
    """The signature of the thinking content, if available."""

    thinking: str
    """The thoughts or reasoning of the assistant."""


@dataclass(kw_only=True)
class ThinkingStartChunk:
    """Represents the start of a thinking chunk stream."""

    type: Literal["thinking_start_chunk"] = "thinking_start_chunk"

    content_type: Literal["thinking"] = "thinking"
    """The type of content reconstructed by this chunk."""


@dataclass(kw_only=True)
class ThinkingChunk:
    """Represents an incremental thinking chunk in a stream."""

    type: Literal["thinking_chunk"] = "thinking_chunk"

    content_type: Literal["thinking"] = "thinking"
    """The type of content reconstructed by this chunk."""

    delta: str
    """The incremental thoughts added in this chunk."""


@dataclass(kw_only=True)
class ThinkingEndChunk:
    """Represents the end of a thinking chunk stream."""

    type: Literal["thinking_end_chunk"] = "thinking_end_chunk"

    content_type: Literal["thinking"] = "thinking"
    """The type of content reconstructed by this chunk."""

    signature: str | None
    """The signature of the thinking content, if available."""
