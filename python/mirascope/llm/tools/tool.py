"""Tool interface for LLM interactions.

This module defines interfaces for tools that can be used by LLMs during a call.
Tools are defined using the `@tool()` decorator which creates a `ToolDef`. When an
LLM uses a tool during a call, a `Tool` instance is created with the specific
arguments provided by the LLM.
"""

from dataclasses import dataclass
from typing import Generic

from ..content import ToolOutput
from ..context import DepsT
from ..types import Jsonable, P, ToolReturnT
from .context_tool_def import ContextToolDef
from .tool_def import ToolDef


@dataclass
class Tool(Generic[P, ToolReturnT, DepsT]):
    """Tool instance with arguments provided by an LLM.

    When an LLM uses a tool during a call, a Tool instance is created with the specific
    arguments provided by the LLM.
    """

    name: str
    """The name of the tool being called."""

    args: dict[str, Jsonable]
    """The arguments provided by the LLM for this tool call."""

    id: str
    """Unique identifier for this tool call."""

    tool_def: ToolDef[P, ToolReturnT] | ContextToolDef[P, ToolReturnT, DepsT]

    """The ToolDef that defines the tool being called."""

    def call(self) -> ToolOutput[ToolReturnT]:
        """Execute the tool with the arguments provided by the LLM.

        Returns:
            The `ToolOutput` result of executing the tool with the provided arguments.

        Raises:
            InvalidArgumentsError: If the arguments provided by the LLM are invalid.
        """
        raise NotImplementedError()
