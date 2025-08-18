"""The `llm.context_tool` decorator for turning functions into context tools."""

import inspect
from dataclasses import dataclass
from typing import overload

from typing_extensions import TypeIs

from ..context import RequiredDepsT
from ..types import JsonableCovariantT, P
from .context_tool import AsyncContextTool, ContextTool
from .protocols import AsyncContextToolFn, ContextToolFn


def _is_async_context_tool_fn(
    fn: ContextToolFn[RequiredDepsT, P, JsonableCovariantT]
    | AsyncContextToolFn[RequiredDepsT, P, JsonableCovariantT],
) -> TypeIs[AsyncContextToolFn[RequiredDepsT, P, JsonableCovariantT]]:
    return inspect.iscoroutinefunction(fn)


@dataclass(kw_only=True)
class ContextToolDecorator:
    """Protocol for the context tool decorator."""

    strict: bool
    """Whether to use strict tool calling, if supported by the provider."""

    @overload
    def __call__(
        self, fn: ContextToolFn[RequiredDepsT, P, JsonableCovariantT]
    ) -> ContextTool[RequiredDepsT, P, JsonableCovariantT]:
        """Call the decorator with a sync function."""
        ...

    @overload
    def __call__(
        self, fn: AsyncContextToolFn[RequiredDepsT, P, JsonableCovariantT]
    ) -> AsyncContextTool[RequiredDepsT, P, JsonableCovariantT]:
        """Call the decorator with an async function."""
        ...

    def __call__(
        self,
        fn: ContextToolFn[RequiredDepsT, P, JsonableCovariantT]
        | AsyncContextToolFn[RequiredDepsT, P, JsonableCovariantT],
    ) -> (
        ContextTool[RequiredDepsT, P, JsonableCovariantT]
        | AsyncContextTool[RequiredDepsT, P, JsonableCovariantT]
    ):
        """Call the decorator with a function."""
        if _is_async_context_tool_fn(fn):
            return AsyncContextTool[RequiredDepsT, P, JsonableCovariantT](
                fn, strict=self.strict, is_context_tool=True
            )
        else:
            return ContextTool[RequiredDepsT, P, JsonableCovariantT](
                fn, strict=self.strict, is_context_tool=True
            )


@overload
def context_tool(
    __fn: ContextToolFn[RequiredDepsT, P, JsonableCovariantT],
) -> ContextTool[RequiredDepsT, P, JsonableCovariantT]:
    """Overload for no arguments, which uses default settings."""
    ...


@overload
def context_tool(
    __fn: AsyncContextToolFn[RequiredDepsT, P, JsonableCovariantT],
) -> AsyncContextTool[RequiredDepsT, P, JsonableCovariantT]:
    """Overload for async functions with no arguments."""
    ...


@overload
def context_tool(*, strict: bool = False) -> ContextToolDecorator:
    """Overload for producing the decorator."""
    ...


def context_tool(
    __fn: ContextToolFn[RequiredDepsT, P, JsonableCovariantT]
    | AsyncContextToolFn[RequiredDepsT, P, JsonableCovariantT]
    | None = None,
    *,
    deps_type: type[RequiredDepsT] | type[None] | None = None,
    strict: bool = False,
) -> (
    ContextTool[RequiredDepsT, P, JsonableCovariantT]
    | AsyncContextTool[RequiredDepsT, P, JsonableCovariantT]
    | ContextToolDecorator
):
    '''Decorator that turns a function into a context tool definition.

    This decorator creates a `ContextTool` that can be used with `llm.call`.
    The function's name, docstring, and type hints are used to generate the
    tool's metadata.

    Args:
        strict: Whether the tool should use strict mode when supported by the model.
        deps_type: Type hint for dependencies (mainly for documentation).

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
            return ctx.deps.books
        ```
    '''

    decorator = ContextToolDecorator(strict=strict)
    if __fn is None:
        return decorator
    return decorator(__fn)
