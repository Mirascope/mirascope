"""The `llm.tool` decorator for turning functions into tools."""

from collections.abc import Callable
from typing import Protocol, overload

from ..context import Context, DepsT
from ..types import P, ToolCovariantT, ToolReturnT
from .context_tool_def import ContextToolDef
from .tool_def import ToolDef


class ToolFn(Protocol[P, ToolCovariantT]):
    """Protocol for the tool function."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> ToolCovariantT:
        """Call the function with the given arguments."""
        ...


class ContextToolFn(Protocol[P, ToolCovariantT, DepsT]):
    """Protocol for the context tool function."""

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> ToolCovariantT:
        """Call the function with the given arguments."""
        ...


class ToolDecorator(Protocol):
    """Protocol for the tool decorator."""

    def __call__(self, fn: ToolFn[P, ToolReturnT]) -> ToolDef[P, ToolReturnT]:
        """Call the decorator with a function."""
        ...


class ContextToolDecorator(Protocol[DepsT]):
    """Protocol for the context tool decorator."""

    def __call__(
        self, fn: ContextToolFn[P, ToolReturnT, DepsT]
    ) -> ContextToolDef[P, ToolReturnT, DepsT]:
        """Call the decorator with a function."""
        ...


@overload
def tool(__fn: ToolFn[P, ToolReturnT]) -> ToolDef[P, ToolReturnT]:
    """Overload for no arguments, which uses default settings."""
    ...


@overload
def tool(*, deps_type: type[None] | None = None, strict: bool = False) -> ToolDecorator:
    """Overload for setting non-default arguments."""
    ...


@overload
def tool(
    *, deps_type: type[DepsT], strict: bool = False
) -> ContextToolDecorator[DepsT]:
    """Overload for tools with context."""
    ...


def tool(
    __fn: Callable[P, ToolReturnT] | None = None,
    *,
    deps_type: type[DepsT] | type[None] | None = None,
    strict: bool = False,
) -> ToolDef[P, ToolReturnT] | ToolDecorator | ContextToolDecorator[DepsT]:
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
