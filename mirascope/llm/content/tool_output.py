"""The `ToolOutput` content class."""

from dataclasses import dataclass
from typing import Generic, Literal, TypeVar

from ..types import Jsonable

R = TypeVar("R", bound=Jsonable)


@dataclass(kw_only=True)
class ToolOutput(Generic[R]):
    """Tool output content for a message.

    Represents the output from a tool call. This is part of a user message's
    content, typically following a tool call from the assistant.
    """

    type: Literal["tool_response"] = "tool_response"

    id: str
    """The ID of the tool call that this output is for."""

    value: R
    """The output value from the tool call."""
