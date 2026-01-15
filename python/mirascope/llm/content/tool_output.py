"""The `ToolOutput` content class."""

from dataclasses import dataclass
from typing import Generic, Literal

from ..types import JsonableCovariantT


@dataclass(kw_only=True)
class ToolOutput(Generic[JsonableCovariantT]):
    """Tool output content for a message.

    Represents the output from a tool call. This is part of a user message's
    content, typically following a tool call from the assistant.
    """

    type: Literal["tool_output"] = "tool_output"

    id: str
    """The ID of the tool call that this output is for."""

    name: str
    """The name of the tool that created this output."""

    value: JsonableCovariantT
    """The output value from the tool call."""
