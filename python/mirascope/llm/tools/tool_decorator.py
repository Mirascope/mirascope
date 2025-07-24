"""The `llm.tool` decorator for turning functions into tools."""

from collections.abc import Awaitable, Callable
from typing import Protocol, overload

from ..context import DepsT
from ..types import JsonableCovariantT, P
from .tool import AsyncTool, Tool


class ToolFn(Protocol[P, JsonableCovariantT]):
    """Protocol for the tool function."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> JsonableCovariantT:
        """Call the function with the given arguments."""
        ...


class AsyncToolFn(Protocol[P, JsonableCovariantT]):
    """Protocol for the async tool function."""

    def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Awaitable[JsonableCovariantT]:
        """Call the function with the given arguments."""
        ...


class ToolDecorator(Protocol):
    """Protocol for the tool decorator."""

    @overload
    def __call__(
        self, fn: ToolFn[P, JsonableCovariantT]
    ) -> Tool[P, JsonableCovariantT]:
        """Call the decorator with a sync function."""
        ...

    @overload
    def __call__(
        self, fn: AsyncToolFn[P, JsonableCovariantT]
    ) -> AsyncTool[P, JsonableCovariantT]:
        """Call the decorator with an async function."""
        ...

    def __call__(
        self, fn: ToolFn[P, JsonableCovariantT] | AsyncToolFn[P, JsonableCovariantT]
    ) -> Tool[P, JsonableCovariantT] | AsyncTool[P, JsonableCovariantT]:
        """Call the decorator with a function."""
        ...


@overload
def tool(__fn: ToolFn[P, JsonableCovariantT]) -> Tool[P, JsonableCovariantT]:
    """Overload for no arguments, which uses default settings."""
    ...


@overload
def tool(__fn: AsyncToolFn[P, JsonableCovariantT]) -> AsyncTool[P, JsonableCovariantT]:
    """Overload for async functions with no arguments."""
    ...


@overload
def tool(*, deps_type: type[None] | None = None, strict: bool = False) -> ToolDecorator:
    """Overload for setting non-default arguments."""
    ...


def tool(
    __fn: Callable[P, JsonableCovariantT]
    | Callable[P, Awaitable[JsonableCovariantT]]
    | None = None,
    *,
    deps_type: type[DepsT] | type[None] | None = None,
    strict: bool = False,
) -> Tool[P, JsonableCovariantT] | AsyncTool[P, JsonableCovariantT] | ToolDecorator:
    '''Decorator that turns a function into a tool definition.

    This decorator creates a `Tool` that can be used with `llm.call`.
    The function's name, docstring, and type hints are used to generate the
    tool's metadata.

    Args:
        strict: Whether the tool should use strict mode when supported by the model.

    Returns:
        A decorator function that converts the function into a Tool.

    Example:

        ```python
        from mirascope import llm

        @llm.tool
        def available_books() -> list[str]:
            """Returns the list of available books."""
            return ["The Name of the Wind"]
        ```
    '''
    raise NotImplementedError()
