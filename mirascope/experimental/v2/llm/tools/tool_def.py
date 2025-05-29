"""The `ToolDef` class for defining tools that LLMs can request be called."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, ParamSpec, TypeGuard

from typing_extensions import TypeVar

from ..types import Jsonable
from .base_tool import BaseTool
from .base_tool_def import BaseToolDef

if TYPE_CHECKING:
    from .tool import Tool

P = ParamSpec("P")
R = TypeVar("R", bound=Jsonable)
DepsT = TypeVar("DepsT", default=None)


@dataclass
class ToolDef(BaseToolDef[P, R]):
    """Protocol defining a tool that can be used by LLMs.

    A ToolDef represents a function that can be called by an LLM during a call.
    It includes metadata like name, description, and parameter schema.

    This class is not instantiated directly but created by the `@tool()` decorator.
    """

    fn: Callable[P, R]
    """The function that implements the tool's functionality."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Call the tool with the provided arguments.

        Args:
            *args: Positional arguments to pass to the tool function.
            **kwargs: Keyword arguments to pass to the tool function.
        Returns:
            The result of calling the tool function with the provided arguments.
        """
        return self.fn(*args, **kwargs)

    def defines(self, tool: BaseTool) -> TypeGuard[Tool[P, R]]:
        """Check if this ToolDef matches a specific Tool instance.

        This method is used to ensure that the ToolDef was created from a specific
        function, allowing for type-safe access to the return value when calling
        the tool.

        Args:
            tool: The Tool instance to compare against.

        Returns:
            True if the ToolDef defines the Tool instance, False otherwise.
        """
        # Check if `self.fn` defines the given `tool`
        raise NotImplementedError()
