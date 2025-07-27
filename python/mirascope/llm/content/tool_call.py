"""The `ToolCall` content class."""

from dataclasses import dataclass
from typing import Literal

from ..types import Jsonable


@dataclass(kw_only=True)
class ToolCall:
    """Tool call content for a message.

    Represents a request from the assistant to call a tool. This is part of
    an assistant message's content.
    """

    type: Literal["tool_call"] = "tool_call"

    id: str
    """A unique identifier for this tool call."""

    name: str
    """The name of the tool to call."""

    args: dict[str, Jsonable]
    """The arguments to pass to the tool."""


@dataclass(kw_only=True)
class ToolCallChunk:
    """Streaming tool call content chunk."""

    type: Literal["tool_call_chunk"] = "tool_call_chunk"

    id: str
    """A unique identifier for this tool call."""

    name: str
    """The name of the tool to call."""

    delta: str
    """The incremental delta to JSON arguments present in this particular chunk."""

    final: bool
    """Whether this is the final piece of content in its sequence. If true, this content's partial is finished generating."""

    def __repr__(self) -> str:
        """Strategic representation for clean default printing."""
        return self.delta
