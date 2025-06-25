"""ContextTool interface for LLM interactions with context.

This module defines interfaces for tools with context that can be used by LLMs during a
call. ContextTools are defined using the `@tool(deps_type=...)` decorator which creates
a `ContextToolDef`. When an LLM uses a tool during a call, a `Tool` instance is created
with the specific arguments provided by the LLM.
"""

from dataclasses import dataclass
from typing import Generic, ParamSpec

from typing_extensions import TypeVar

from ..content import ToolOutput
from ..context import Context
from ..types import Jsonable
from .base_tool import BaseTool
from .context_tool_def import ContextToolDef

P = ParamSpec("P")
R = TypeVar("R", bound=Jsonable)
DepsT = TypeVar("DepsT", default=None)


@dataclass
class ContextTool(BaseTool[P, R], Generic[P, R, DepsT]):
    """Tool instance with arguments provided by an LLM.

    When an LLM uses a tool during a call, a Tool instance is created with the specific
    arguments provided by the LLM.
    """

    tool_def: ContextToolDef[P, R, DepsT]
    """The ContextToolDef that defines the tool being called."""

    def call(self, ctx: Context[DepsT]) -> ToolOutput[R]:
        """Execute the tool with context and the arguments provided by the LLM.

        Returns:
            The `ToolOutput` result of executing the tool with the provided arguments.

        Raises:
            InvalidArgumentsError: If the arguments provided by the LLM are invalid.
        """
        raise NotImplementedError()
