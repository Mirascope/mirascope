"""Tool interface for LLM interactions.

This module defines interfaces for tools that can be used by LLMs during a call.
Tools are defined using the `@tool()` decorator which creates a `ToolDef`. When an
LLM uses a tool during a call, a `Tool` instance is created with the specific
arguments provided by the LLM.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import (
    Any,
    Generic,
    Literal,
    ParamSpec,
    Protocol,
    TypeGuard,
    TypeVar,
    overload,
)

from .messages import JsonableType

__all__ = [
    "Tool",
    "ToolDef",
    "ToolOutput",
    "tool",
]

P = ParamSpec("P")
R = TypeVar("R", bound=JsonableType)
T = TypeVar("T", bound=JsonableType)


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


@dataclass
class Tool(Generic[R]):
    """Tool instance with arguments provided by an LLM.

    When an LLM uses a tool during a call, a Tool instance is created with the specific
    arguments provided by the LLM.
    """

    tool_def: ToolDef[..., R]
    """The ToolDef that defines the tool being called."""

    name: str
    """The name of the tool being called."""

    args: dict[str, JsonableType]
    """The arguments provided by the LLM for this tool call."""

    id: str
    """Unique identifier for this tool call."""

    def call(self) -> ToolOutput[R]:
        """Execute the tool with the arguments provided by the LLM.

        Returns:
            The `ToolOutput` result of executing the tool with the provided arguments.

        Raises:
            InvalidArgumentsError: If the arguments provided by the LLM are invalid.
        """
        raise NotImplementedError()


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


@overload
def tool(__fn: Callable[P, R]) -> ToolDef[P, R]:
    """Overload for no arguments, which uses default settings."""


@overload
def tool(*, strict: bool = False) -> Callable[[Callable[P, R]], ToolDef[P, R]]:
    """Overload for setting non-default arguments."""


def tool(
    __fn=None, *, strict: bool = False
) -> ToolDef[P, R] | Callable[[Callable[P, R]], ToolDef[P, R]]:
    '''Decorator that turns a function into a tool definition.

    This decorator creates a `ToolDef` that can be used with `llm.call`.
    The function's name, docstring, and type hints are used to generate the
    tool's metadata.

    Args:
        strict: Whether the tool should use strict mode when supported by the model.

    Returns:
        A decorator function that converts the function into a ToolDef.

    Example:

        ```python
        from mirascope import llm

        @llm.tool()
        def available_books() -> list[str]:
            """Returns the list of available books."""
            return ["The Name of the Wind"]
        ```
    '''
    raise NotImplementedError()
