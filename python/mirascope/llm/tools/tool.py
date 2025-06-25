"""Tool interface for LLM interactions.

This module defines interfaces for tools that can be used by LLMs during a call.
Tools are defined using the `@tool()` decorator which creates a `ToolDef`. When an
LLM uses a tool during a call, a `Tool` instance is created with the specific
arguments provided by the LLM.
"""

from dataclasses import dataclass
from typing import ParamSpec, TypeVar

from ..content import ToolOutput
from ..types import Jsonable
from .base_tool import BaseTool
from .tool_def import ToolDef

P = ParamSpec("P")
R = TypeVar("R", bound=Jsonable)


@dataclass
class Tool(BaseTool[P, R]):
    """Tool instance with arguments provided by an LLM.

    When an LLM uses a tool during a call, a Tool instance is created with the specific
    arguments provided by the LLM.
    """

    tool_def: ToolDef[P, R]
    """The ToolDef that defines the tool being called."""

    def call(self) -> ToolOutput[R]:
        """Execute the tool with the arguments provided by the LLM.

        Returns:
            The `ToolOutput` result of executing the tool with the provided arguments.

        Raises:
            InvalidArgumentsError: If the arguments provided by the LLM are invalid.
        """
        raise NotImplementedError()
