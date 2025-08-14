"""The `llm.tool` decorator for turning functions into tools."""

from collections.abc import Awaitable
from typing import Protocol, overload

from ..context import Context, DepsT
from ..types import JsonableCovariantT, P
from .context_tool import AsyncContextTool, ContextTool


class ContextToolFn(Protocol[P, JsonableCovariantT, DepsT]):
    """Protocol for the context tool function."""

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> JsonableCovariantT:
        """Call the function with the given arguments."""
        raise NotImplementedError()


class AsyncContextToolFn(Protocol[P, JsonableCovariantT, DepsT]):
    """Protocol for the async context tool function."""

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Awaitable[JsonableCovariantT]:
        """Call the function with the given arguments."""
        raise NotImplementedError()


class ContextToolDecorator:
    """Protocol for the context tool decorator."""

    @overload
    def __call__(
        self, fn: ContextToolFn[P, JsonableCovariantT, DepsT]
    ) -> ContextTool[DepsT, P, JsonableCovariantT]:
        """Call the decorator with a sync function."""
        ...

    @overload
    def __call__(
        self, fn: AsyncContextToolFn[P, JsonableCovariantT, DepsT]
    ) -> AsyncContextTool[DepsT, P, JsonableCovariantT]:
        """Call the decorator with an async function."""
        ...

    def __call__(
        self,
        fn: ContextToolFn[P, JsonableCovariantT, DepsT]
        | AsyncContextToolFn[P, JsonableCovariantT, DepsT],
    ) -> (
        ContextTool[DepsT, P, JsonableCovariantT]
        | AsyncContextTool[DepsT, P, JsonableCovariantT]
    ):
        """Call the decorator with a function."""
        raise NotImplementedError()


@overload
def context_tool(
    __fn: ContextToolFn[P, JsonableCovariantT, DepsT],
) -> ContextTool[DepsT, P, JsonableCovariantT]:
    """Overload for no arguments, which uses default settings."""
    ...


@overload
def context_tool(
    __fn: AsyncContextToolFn[P, JsonableCovariantT, DepsT],
) -> AsyncContextTool[DepsT, P, JsonableCovariantT]:
    """Overload for async functions with no arguments."""
    ...


@overload
def context_tool(*, strict: bool = False) -> ContextToolDecorator:
    """Overload for producing the decorator."""
    ...


def context_tool(
    __fn: ContextToolFn[P, JsonableCovariantT, DepsT]
    | AsyncContextToolFn[P, JsonableCovariantT, DepsT]
    | None = None,
    *,
    deps_type: type[DepsT] | type[None] | None = None,
    strict: bool = False,
) -> (
    ContextTool[DepsT, P, JsonableCovariantT]
    | AsyncContextTool[DepsT, P, JsonableCovariantT]
    | ContextToolDecorator
):
    '''Decorator that turns a function into a tool definition.

    This decorator creates a `ContextTool` that can be used with `llm.call`.
    The function's name, docstring, and type hints are used to generate the
    tool's metadata.

    Args:
        strict: Whether the tool should use strict mode when supported by the model.

    Returns:
        A decorator function that converts the function into a ContextTool.

    Example:

        ```python
        from dataclasses import dataclass

        from mirascope import llm


        @dataclass
        class Library:
            books: list[str]


        library = Library(books=["Mistborn", "Gödel, Escher, Bach", "Dune"])

        @llm.context_tool
        def available_books(ctx: llm.Context[Library]) -> list[str]:
            """Returns the list of available books."""
            return ctx.deps.available_books
        ```
    '''
    raise NotImplementedError()
