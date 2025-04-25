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
