"""The `llm.tool` decorator for turning functions into tools."""

from dataclasses import dataclass
from typing import overload

from ..context import DepsT
from ..types import JsonableCovariantT, P
from . import _utils as _tool_utils
from .protocols import AsyncContextToolFn, AsyncToolFn, ContextToolFn, ToolFn
from .tools import AsyncContextTool, AsyncTool, ContextTool, Tool


@dataclass(kw_only=True)
class ToolDecorator:
    """Protocol for the tool decorator."""

    strict: bool
    """Whether to use strict tool calling, if supported by the provider."""

    @overload
    def __call__(  # pyright:ignore[reportOverlappingOverload]
        self, fn: ContextToolFn[DepsT, P, JsonableCovariantT]
    ) -> ContextTool[DepsT, JsonableCovariantT, P]:
        """Call the decorator with a context function."""
        ...

    @overload
    def __call__(  # pyright:ignore[reportOverlappingOverload]
        self, fn: AsyncContextToolFn[DepsT, P, JsonableCovariantT]
    ) -> AsyncContextTool[DepsT, JsonableCovariantT, P]:
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
        ContextTool[DepsT, JsonableCovariantT, P]
        | AsyncContextTool[DepsT, JsonableCovariantT, P]
        | Tool[P, JsonableCovariantT]
        | AsyncTool[P, JsonableCovariantT]
    ):
        """Call the decorator with a function."""
        is_context = _tool_utils.is_context_tool_fn(fn)
        is_async = _tool_utils.is_async_tool_fn(fn)

        if is_context and is_async:
            return AsyncContextTool[DepsT, JsonableCovariantT, P](
                fn, strict=self.strict
            )
        elif is_context:
            return ContextTool[DepsT, JsonableCovariantT, P](fn, strict=self.strict)
        elif is_async:
            return AsyncTool[P, JsonableCovariantT](fn, strict=self.strict)
        else:
            return Tool[P, JsonableCovariantT](fn, strict=self.strict)


@overload
def tool(  # pyright:ignore[reportOverlappingOverload]
    __fn: AsyncContextToolFn[DepsT, P, JsonableCovariantT],
) -> AsyncContextTool[DepsT, JsonableCovariantT, P]:
    """Overload for async context tool functions."""
    ...


@overload
def tool(  # pyright:ignore[reportOverlappingOverload]
    __fn: ContextToolFn[DepsT, P, JsonableCovariantT],
) -> ContextTool[DepsT, JsonableCovariantT, P]:
    """Overload for context tool functions."""
    ...


@overload
def tool(__fn: AsyncToolFn[P, JsonableCovariantT]) -> AsyncTool[P, JsonableCovariantT]:
    """Overload for regular async tool functions."""
    ...


@overload
def tool(__fn: ToolFn[P, JsonableCovariantT]) -> Tool[P, JsonableCovariantT]:
    """Overload for regular sync tool functions."""
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
    ContextTool[DepsT, JsonableCovariantT, P]
    | AsyncContextTool[DepsT, JsonableCovariantT, P]
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
