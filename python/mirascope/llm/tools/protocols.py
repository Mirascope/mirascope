from typing import Protocol

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
