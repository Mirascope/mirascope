from typing import Any, Protocol

from ..context import Context, DepsT
from ..types import JsonableCovariantT, P


class ToolFn(Protocol[P, JsonableCovariantT]):
    """Protocol for the tool function."""

    __name__: str
    """The name of the tool."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> JsonableCovariantT:
        """Call the function with the given arguments."""
        raise NotImplementedError()


class AsyncToolFn(Protocol[P, JsonableCovariantT]):
    """Protocol for the async tool function."""

    __name__: str
    """The name of the tool."""

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> JsonableCovariantT:
        """Call the function with the given arguments."""
        raise NotImplementedError()


class ContextToolFn(Protocol[DepsT, P, JsonableCovariantT]):
    """Protocol for the context tool function."""

    __name__: str
    """The name of the tool."""

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> JsonableCovariantT:
        """Call the function with the given arguments."""
        raise NotImplementedError()


class AsyncContextToolFn(Protocol[DepsT, P, JsonableCovariantT]):
    """Protocol for the async context tool function."""

    __name__: str
    """The name of the tool."""

    async def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> JsonableCovariantT:
        """Call the function with the given arguments."""
        raise NotImplementedError()


class KwargsCallable(Protocol[JsonableCovariantT]):
    """Protocol for functions that can be called with `Any`-typed kwargs.

    Used internally to type-cast tool functions for compatibility with
    json.loads() output when executing tool calls.
    """

    def __call__(self, **kwargs: dict[str, Any]) -> JsonableCovariantT: ...


class AsyncKwargsCallable(Protocol[JsonableCovariantT]):
    """Protocol for async functions that can be called with `Any`-typed kwargs.

    Used internally to type-cast async tool functions for compatibility with
    json.loads() output when executing tool calls.
    """

    async def __call__(self, **kwargs: dict[str, Any]) -> JsonableCovariantT: ...


class ContextKwargsCallable(Protocol[DepsT, JsonableCovariantT]):
    """Protocol for context functions that can be called with `Any`-typed kwargs.

    Used internally to type-cast context tool functions for compatibility with
    json.loads() output when executing tool calls.
    """

    def __call__(
        self, ctx: Context[DepsT], **kwargs: dict[str, Any]
    ) -> JsonableCovariantT: ...


class AsyncJsonKwargsCallable(Protocol[DepsT, JsonableCovariantT]):
    """Protocol for async context functions that can be called with `Any`-typed kwargs.

    Used internally to type-cast async context tool functions for compatibility with
    json.loads() output when executing tool calls.
    """

    async def __call__(
        self, ctx: Context[DepsT], **kwargs: dict[str, Any]
    ) -> JsonableCovariantT: ...
