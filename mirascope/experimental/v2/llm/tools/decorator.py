"""The `llm.tool` decorator for turning functions into tools."""

from collections.abc import Callable
from typing import ParamSpec, TypeVar, overload

from ..types import Jsonable
from .tool_def import ToolDef

P = ParamSpec("P")
R = TypeVar("R", bound=Jsonable)
T = TypeVar("T", bound=Jsonable)


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
