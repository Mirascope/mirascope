"""The `llm.tool` decorator for turning functions into tools."""

import inspect
from dataclasses import dataclass
from typing import overload
from typing_extensions import TypeIs

from ..types import JsonableCovariantT, P
from .protocols import AsyncToolFn, ToolFn
from .tool import AsyncTool, Tool


@dataclass(kw_only=True)
class ToolDecorator:
    """Protocol for the tool decorator."""

    strict: bool
    """Whether to use strict tool calling, if supported by the provider."""

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
        if _is_async_tool_fn(fn):
            return AsyncTool[P, JsonableCovariantT](fn, strict=self.strict)
        else:
            return Tool[P, JsonableCovariantT](fn, strict=self.strict)


def _is_async_tool_fn(
    fn: ToolFn | AsyncToolFn,
) -> TypeIs[AsyncToolFn[P, JsonableCovariantT]]:
    return inspect.iscoroutinefunction(fn)


@overload
def tool(__fn: ToolFn[P, JsonableCovariantT]) -> Tool[P, JsonableCovariantT]:
    """Overload for no arguments, which uses default settings."""
    ...


@overload
def tool(__fn: AsyncToolFn[P, JsonableCovariantT]) -> AsyncTool[P, JsonableCovariantT]:
    """Overload for async functions with no arguments."""
    ...


@overload
def tool(*, strict: bool = False) -> ToolDecorator:
    """Overload for setting non-default arguments."""
    ...


def tool(
    __fn: ToolFn[P, JsonableCovariantT]
    | AsyncToolFn[P, JsonableCovariantT]
    | None = None,
    *,
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
    decorator = ToolDecorator(strict=strict)
    if __fn is None:
        return decorator
    return decorator(__fn)
