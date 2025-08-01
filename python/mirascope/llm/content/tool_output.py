"""The `ToolOutput` content class."""

from dataclasses import dataclass
from typing import Generic, Literal

from ..types import JsonableT


@dataclass(kw_only=True)
class ToolOutput(Generic[JsonableT]):
    """Tool output content for a message.

    Represents the output from a tool call. This is part of a user message's
    content, typically following a tool call from the assistant.
    """

    type: Literal["tool_output"] = "tool_output"

    content_type: Literal["tool_output"] = "tool_output"
    """The type of content being represented."""

    id: str
    """The ID of the tool call that this output is for."""

    value: JsonableT
    """The output value from the tool call."""
