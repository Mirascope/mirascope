"""The `llm.tool` decorator for turning functions into tools."""

import inspect
from dataclasses import dataclass
from typing import overload
from typing_extensions import TypeIs

from ..context import DepsT, _utils as _context_utils
from ..types import JsonableCovariantT, P
from .context_tool import AsyncContextTool, ContextTool
from .protocols import AsyncContextToolFn, AsyncToolFn, ContextToolFn, ToolFn
from .tool import AsyncTool, Tool


@dataclass(kw_only=True)
class ToolDecorator:
    """Protocol for the tool decorator."""

    strict: bool
    """Whether to use strict tool calling, if supported by the provider."""

    @overload
    def __call__(  # pyright:ignore[reportOverlappingOverload]
        self, fn: ContextToolFn[DepsT, P, JsonableCovariantT]
    ) -> ContextTool[DepsT, P, JsonableCovariantT]:
        """Call the decorator with a context function."""
        ...

    @overload
    def __call__(  # pyright:ignore[reportOverlappingOverload]
        self, fn: AsyncContextToolFn[DepsT, P, JsonableCovariantT]
    ) -> AsyncContextTool[DepsT, P, JsonableCovariantT]:
        """Call the decorator with an async context function."""
        ...

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
        self,
        fn: ContextToolFn[DepsT, P, JsonableCovariantT]
        | AsyncContextToolFn[DepsT, P, JsonableCovariantT]
        | ToolFn[P, JsonableCovariantT]
        | AsyncToolFn[P, JsonableCovariantT],
    ) -> (
        ContextTool[DepsT, P, JsonableCovariantT]
        | AsyncContextTool[DepsT, P, JsonableCovariantT]
        | Tool[P, JsonableCovariantT]
        | AsyncTool[P, JsonableCovariantT]
    ):
        """Call the decorator with a function."""
        if _is_context_tool_fn(fn):
            if _is_async_context_tool_fn(fn):
                return AsyncContextTool[DepsT, P, JsonableCovariantT](
                    fn, strict=self.strict, is_context_tool=True
                )
            else:
                return ContextTool[DepsT, P, JsonableCovariantT](
                    fn, strict=self.strict, is_context_tool=True
                )
        elif _is_async_tool_fn(fn):
            return AsyncTool[P, JsonableCovariantT](fn, strict=self.strict)
        else:
            return Tool[P, JsonableCovariantT](fn, strict=self.strict)


def _is_async_tool_fn(
    fn: ToolFn | AsyncToolFn,
) -> TypeIs[AsyncToolFn[P, JsonableCovariantT]]:
    return inspect.iscoroutinefunction(fn)


def _is_context_tool_fn(
    fn: ContextToolFn[DepsT, P, JsonableCovariantT]
    | AsyncContextToolFn[DepsT, P, JsonableCovariantT]
    | ToolFn[P, JsonableCovariantT]
    | AsyncToolFn[P, JsonableCovariantT],
) -> TypeIs[
    ContextToolFn[DepsT, P, JsonableCovariantT]
    | AsyncContextToolFn[DepsT, P, JsonableCovariantT]
]:
    """Return whether a ToolFn is interpreted as a context tool."""
    return _context_utils.first_param_is_context(fn)


def _is_async_context_tool_fn(
    fn: ContextToolFn[DepsT, P, JsonableCovariantT]
    | AsyncContextToolFn[DepsT, P, JsonableCovariantT],
) -> TypeIs[AsyncContextToolFn[DepsT, P, JsonableCovariantT]]:
    return inspect.iscoroutinefunction(fn)


@overload
def tool(  # pyright:ignore[reportOverlappingOverload]
    __fn: ContextToolFn[DepsT, P, JsonableCovariantT],
) -> ContextTool[DepsT, P, JsonableCovariantT]:
    """Overload for context tool functions."""
    ...


@overload
def tool(  # pyright:ignore[reportOverlappingOverload]
    __fn: AsyncContextToolFn[DepsT, P, JsonableCovariantT],
) -> AsyncContextTool[DepsT, P, JsonableCovariantT]:
    """Overload for async context tool functions."""
    ...


@overload
def tool(__fn: ToolFn[P, JsonableCovariantT]) -> Tool[P, JsonableCovariantT]:
    """Overload for regular sync tool functions."""
    ...


@overload
def tool(__fn: AsyncToolFn[P, JsonableCovariantT]) -> AsyncTool[P, JsonableCovariantT]:
    """Overload for regular async tool functions."""
    ...


@overload
def tool(*, strict: bool = False) -> ToolDecorator:
    """Overload for setting non-default arguments."""
    ...


def tool(
    __fn: ContextToolFn[DepsT, P, JsonableCovariantT]
    | AsyncContextToolFn[DepsT, P, JsonableCovariantT]
    | ToolFn[P, JsonableCovariantT]
    | AsyncToolFn[P, JsonableCovariantT]
    | None = None,
    *,
    strict: bool = False,
) -> (
    ContextTool[DepsT, P, JsonableCovariantT]
    | AsyncContextTool[DepsT, P, JsonableCovariantT]
    | Tool[P, JsonableCovariantT]
    | AsyncTool[P, JsonableCovariantT]
    | ToolDecorator
):
    '''Decorator that turns a function into a tool definition.

    This decorator creates a `Tool` or `ContextTool` that can be used with `llm.call`.
    The function's name, docstring, and type hints are used to generate the
    tool's metadata.

    If the first parameter is named 'ctx' or typed as `llm.Context[T]`, it creates
    a ContextTool. Otherwise, it creates a regular Tool.

    Args:
        strict: Whether the tool should use strict mode when supported by the model.

    Returns:
        A decorator function that converts the function into a Tool or ContextTool.

    Examples:

        Regular tool:
        ```python
        from mirascope import llm

        @llm.tool
        def available_books() -> list[str]:
            """Returns the list of available books."""
            return ["The Name of the Wind"]
        ```

        Context tool:
        ```python
        from dataclasses import dataclass

        from mirascope import llm


        @dataclass
        class Library:
            books: list[str]


        library = Library(books=["Mistborn", "Gödel, Escher, Bach", "Dune"])

        @llm.tool
        def available_books(ctx: llm.Context[Library]) -> list[str]:
            """Returns the list of available books."""
            return ctx.deps.books
        ```
    '''
    decorator = ToolDecorator(strict=strict)
    if __fn is None:
        return decorator
    return decorator(__fn)
