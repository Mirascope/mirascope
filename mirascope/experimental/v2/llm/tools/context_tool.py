"""ContextTool interface for LLM interactions with context.

This module defines interfaces for tools with context that can be used by LLMs during a
call. ContextTools are defined using the `@tool(deps_type=...)` decorator which creates
a `ContextToolDef`. When an LLM uses a tool during a call, a `Tool` instance is created
with the specific arguments provided by the LLM.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Concatenate, Generic, ParamSpec

from typing_extensions import TypeVar

from ..content import ToolOutput
from ..contexts import Context
from ..types import Jsonable
from .base_tool import BaseTool

P = ParamSpec("P")
R = TypeVar("R", bound=Jsonable)
DepsT = TypeVar("DepsT", default=None)


@dataclass
class ContextTool(BaseTool[R], Generic[R, DepsT]):
    """Tool instance with arguments provided by an LLM.

    When an LLM uses a tool during a call, a Tool instance is created with the specific
    arguments provided by the LLM.
    """

    fn: Callable[Concatenate[Context[DepsT], ...], R]

    def call(self, ctx: Context[DepsT]) -> ToolOutput[R]:
        """Execute the tool with context and the arguments provided by the LLM.

        Returns:
            The `ToolOutput` result of executing the tool with the provided arguments.

        Raises:
            InvalidArgumentsError: If the arguments provided by the LLM are invalid.
        """
        raise NotImplementedError()
