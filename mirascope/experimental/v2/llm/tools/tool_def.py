"""The `ToolDef` class for defining tools that LLMs can request be called."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, ParamSpec, Protocol, TypeGuard, TypeVar

from ..types import Jsonable
from .tool import Tool

P = ParamSpec("P")
R = TypeVar("R", bound=Jsonable)
T = TypeVar("T", bound=Jsonable)


@dataclass
class ToolDef(Protocol[P, R]):
    """Protocol defining a tool that can be used by LLMs.

    A ToolDef represents a function that can be called by an LLM during a call.
    It includes metadata like name, description, and parameter schema.

    This class is not instantiated directly but created by the `@tool()` decorator.
    """

    fn: Callable[..., R]
    """The function that implements the tool's functionality."""

    name: str
    """The name of the tool, used by the LLM to identify which tool to call."""

    description: str
    """Description of what the tool does, extracted from the function's docstring."""

    parameters: dict[str, Any]
    """JSON Schema describing the parameters accepted by the tool."""

    strict: bool
    """Whether the tool should use strict mode when supported by the model."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Call the tool with the provided arguments.

        Args:
            *args: Positional arguments to pass to the tool function.
            **kwargs: Keyword arguments to pass to the tool function.
        Returns:
            The result of calling the tool function with the provided arguments.
        """
        raise NotImplementedError()

    def defines(self, tool: Tool) -> TypeGuard[Tool[R]]:
        """Check if this ToolDef matches a specific Tool instance.

        This method is used to ensure that the ToolDef was created from a specific
        function, allowing for type-safe access to the return value when calling
        the tool.

        Args:
            tool: The Tool instance to compare against.

        Returns:
            True if the ToolDef defines the Tool instance, False otherwise.
        """
        raise NotImplementedError()
