"""The `ToolOutput` content class."""

from dataclasses import dataclass
from typing import Generic, Literal, cast

from ..exceptions import ToolError
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

    result: JsonableCovariantT | str
    """The result of calling the tool.
    
    If the tool executed successfully, this will be the tool output.
    If the tool errored, this will be the error message, as a string.
    
    In either case, the result should be passed back to the LLM (so it can
    either process the output, or re-try with awareness of the error.)
    """

    error: ToolError | None = None
    """The error from calling the tool, if any."""

    @property
    def output(self) -> JsonableCovariantT:
        if self.error is not None:
            raise self.error
        return cast(JsonableCovariantT, self.result)
