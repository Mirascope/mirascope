"""Traced call wrappers for @ops.trace decorated @llm.call functions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar
from typing_extensions import TypeIs

from ...llm.calls import AsyncCall, AsyncContextCall, Call, ContextCall
from ...llm.context import Context, DepsT
from ...llm.formatting import FormattableT
from ...llm.responses import (
    AsyncContextResponse,
    AsyncContextStreamResponse,
    AsyncResponse,
    AsyncStreamResponse,
    ContextResponse,
    ContextStreamResponse,
    Response,
    StreamResponse,
)
from ...llm.types import P
from .protocols import (
    AsyncFunction,
    R,
    SyncFunction,
)
from .traced_functions import (
    AsyncTrace,
    AsyncTracedContextFunction,
    AsyncTracedFunction,
    Trace,
    TracedContextFunction,
    TracedFunction,
)

CallT = TypeVar(
    "CallT",
    bound=Call[..., Any]
    | AsyncCall[..., Any]
    | ContextCall[..., Any, Any]
    | AsyncContextCall[..., Any, Any],
)


def is_call_type(
    fn: (
        SyncFunction[P, R]
        | AsyncFunction[P, R]
        | ContextCall[P, DepsT, FormattableT]
        | AsyncContextCall[P, DepsT, FormattableT]
        | Call[P, FormattableT]
        | AsyncCall[P, FormattableT]
    ),
) -> TypeIs[
    ContextCall[P, DepsT, FormattableT]
    | AsyncContextCall[P, DepsT, FormattableT]
    | Call[P, FormattableT]
    | AsyncCall[P, FormattableT]
]:
    """Check if fn is any of the Call types."""
    return isinstance(fn, Call | AsyncCall | ContextCall | AsyncContextCall)


def wrap_call(
    fn: (
        ContextCall[P, DepsT, FormattableT]
        | AsyncContextCall[P, DepsT, FormattableT]
        | Call[P, FormattableT]
        | AsyncCall[P, FormattableT]
    ),
    tags: tuple[str, ...],
    metadata: dict[str, str] | None = None,
) -> (
    TracedContextCall[P, DepsT, FormattableT]
    | TracedAsyncContextCall[P, DepsT, FormattableT]
    | TracedCall[P, FormattableT]
    | TracedAsyncCall[P, FormattableT]
):
    """Wrap a Call object with the appropriate TracedCall type."""
    metadata = metadata or {}
    if isinstance(fn, AsyncContextCall):
        return TracedAsyncContextCall(_call=fn, tags=tags, metadata=metadata)
    elif isinstance(fn, ContextCall):
        return TracedContextCall(_call=fn, tags=tags, metadata=metadata)
    elif isinstance(fn, AsyncCall):
        return TracedAsyncCall(_call=fn, tags=tags, metadata=metadata)
    else:
        return TracedCall(_call=fn, tags=tags, metadata=metadata)


@dataclass(kw_only=True)
class _BaseTracedCall(Generic[CallT]):
    """Wrapper for traced Call objects."""

    _call: CallT
    """The original unwrapped Call object."""

    tags: tuple[str, ...]
    """Tags to be associated with traced calls."""

    metadata: dict[str, str] = field(default_factory=dict)
    """Arbitrary key-value pairs for additional metadata."""


@dataclass(kw_only=True)
class TracedCall(_BaseTracedCall[Call[P, FormattableT]]):
    """Traced wrapper for traced synchronous Call objects.

    When @ops.trace decorates an @llm.call, it returns a TracedCall that wraps
    the call and stream methods with tracing capabilities.

    Example:
        ```python
        @ops.trace
        @llm.call("gpt-4o-mini")
        def recommend_book(genre: str):
            return f"Recommend a {genre} book"

        # Returns Response directly (but execution is traced)
        response = recommend_book("fantasy")
        print(response.content)

        # Same as __call__
        response = recommend_book.call("fantasy")

        # Streaming returns StreamResponse (traced)
        stream = recommend_book.stream("fantasy")
        for chunk in stream:
            print(chunk)

        # Use wrapped to get Trace[Response] with span info
        trace = recommend_book.wrapped("fantasy")
        print(trace.result.content)
        print(trace.span_id)

        # Use wrapped_stream to get Trace[StreamResponse]
        trace = recommend_book.wrapped_stream("fantasy")
        ```
    """

    call: TracedFunction[P, Response | Response[FormattableT]] = field(init=False)
    """TracedFunction wrapping the call method."""

    stream: TracedFunction[P, StreamResponse | StreamResponse[FormattableT]] = field(
        init=False
    )
    """TracedFunction wrapping the stream method."""

    def __post_init__(self) -> None:
        """Initialize TracedFunction wrappers for call and stream methods."""
        self.call = TracedFunction(
            fn=self._call.call, tags=self.tags, metadata=self.metadata
        )
        self.stream = TracedFunction(
            fn=self._call.stream, tags=self.tags, metadata=self.metadata
        )

    def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Response | Response[FormattableT]:
        """Call the traced function and return Response directly."""
        return self.call(*args, **kwargs)

    def wrapped(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Trace[Response | Response[FormattableT]]:
        """Call the traced function and return a wrapped Response."""
        return self.call.wrapped(*args, **kwargs)

    def wrapped_stream(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Trace[StreamResponse | StreamResponse[FormattableT]]:
        """Stream the traced function and return a wrapped StreamResponse."""
        return self.stream.wrapped(*args, **kwargs)


@dataclass(kw_only=True)
class TracedAsyncCall(_BaseTracedCall[AsyncCall[P, FormattableT]]):
    """Traced wrapper for traced asynchronous AsyncCall objects.

    Example:
        ```python
        @ops.trace
        @llm.call("gpt-4o-mini")
        async def recommend_book(genre: str):
            return f"Recommend a {genre} book"

        # Returns AsyncResponse directly (but execution is traced)
        response = await recommend_book("fantasy")
        print(response.content)

        # Use wrapped to get AsyncTrace[AsyncResponse] with span info
        trace = await recommend_book.wrapped("fantasy")
        print(trace.result.content)
        print(trace.span_id)
        ```
    """

    call: AsyncTracedFunction[P, AsyncResponse | AsyncResponse[FormattableT]] = field(
        init=False
    )
    """AsyncTracedFunction wrapping the call method."""

    stream: AsyncTracedFunction[
        P, AsyncStreamResponse | AsyncStreamResponse[FormattableT]
    ] = field(init=False)
    """AsyncTracedFunction wrapping the stream method."""

    def __post_init__(self) -> None:
        """Initialize AsyncTracedFunction wrappers for call and stream methods."""
        self.call = AsyncTracedFunction(
            fn=self._call.call, tags=self.tags, metadata=self.metadata
        )
        self.stream = AsyncTracedFunction(
            fn=self._call.stream, tags=self.tags, metadata=self.metadata
        )

    async def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Call the traced function and return AsyncResponse directly."""
        return await self.call(*args, **kwargs)

    async def wrapped(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncTrace[AsyncResponse | AsyncResponse[FormattableT]]:
        """Call the traced function and return a wrapped Response."""
        return await self.call.wrapped(*args, **kwargs)

    async def wrapped_stream(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncTrace[AsyncStreamResponse | AsyncStreamResponse[FormattableT]]:
        """Stream the traced function and return a wrapped StreamResponse."""
        return await self.stream.wrapped(*args, **kwargs)


@dataclass(kw_only=True)
class TracedContextCall(_BaseTracedCall[ContextCall[P, DepsT, FormattableT]]):
    """Traced wrapper for traced synchronous ContextCall objects.

    Example:
        ```python
        @ops.trace
        @llm.call("gpt-4o-mini")
        def recommend_book(ctx: llm.Context[str], genre: str):
            return f"{ctx.deps} Recommend a {genre} book"

        ctx = llm.Context(deps="As a librarian,")

        # Returns ContextResponse directly (but execution is traced)
        response = recommend_book(ctx, "fantasy")
        print(response.content)

        # Use wrapped to get Trace[ContextResponse] with span info
        trace = recommend_book.wrapped(ctx, "fantasy")
        print(trace.result.content)
        ```
    """

    call: TracedContextFunction[
        P, DepsT, ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]
    ] = field(init=False)
    """TracedContextFunction wrapping the call method."""

    stream: TracedContextFunction[
        P,
        DepsT,
        ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT],
    ] = field(init=False)
    """TracedContextFunction wrapping the stream method."""

    def __post_init__(self) -> None:
        """Initialize TracedContextFunction wrappers for call and stream methods."""
        self.call = TracedContextFunction(
            fn=self._call.call, tags=self.tags, metadata=self.metadata
        )
        self.stream = TracedContextFunction(
            fn=self._call.stream, tags=self.tags, metadata=self.metadata
        )

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Call the traced function and return ContextResponse directly."""
        return self.call(ctx, *args, **kwargs)

    def wrapped(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Trace[ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]]:
        """Call the traced function and return a wrapped Response."""
        return self.call.wrapped(ctx, *args, **kwargs)

    def wrapped_stream(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Trace[
        ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]
    ]:
        """Stream the traced function and return a wrapped StreamResponse."""
        return self.stream.wrapped(ctx, *args, **kwargs)


@dataclass(kw_only=True)
class TracedAsyncContextCall(_BaseTracedCall[AsyncContextCall[P, DepsT, FormattableT]]):
    """Traced wrapper for traced asynchronous AsyncContextCall objects.

    Example:
        ```python
        @ops.trace
        @llm.call("gpt-4o-mini")
        async def recommend_book(ctx: llm.Context[str], genre: str):
            return f"{ctx.deps} Recommend a {genre} book"

        ctx = llm.Context(deps="As a librarian,")

        # Returns AsyncContextResponse directly (but execution is traced)
        response = await recommend_book(ctx, "fantasy")
        print(response.content)

        # Use wrapped to get AsyncTrace[AsyncContextResponse] with span info
        trace = await recommend_book.wrapped(ctx, "fantasy")
        print(trace.result.content)
        ```
    """

    call: AsyncTracedContextFunction[
        P,
        DepsT,
        AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT],
    ] = field(init=False)
    """AsyncTracedContextFunction wrapping the call method."""

    stream: AsyncTracedContextFunction[
        P,
        DepsT,
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT],
    ] = field(init=False)
    """AsyncTracedContextFunction wrapping the stream method."""

    def __post_init__(self) -> None:
        """Initialize AsyncTracedContextFunction wrappers for call and stream methods."""
        self.call = AsyncTracedContextFunction(
            fn=self._call.call, tags=self.tags, metadata=self.metadata
        )
        self.stream = AsyncTracedContextFunction(
            fn=self._call.stream, tags=self.tags, metadata=self.metadata
        )

    async def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Call the traced function and return AsyncContextResponse directly."""
        return await self.call(ctx, *args, **kwargs)

    async def wrapped(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncTrace[
        AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]
    ]:
        """Call the traced function and return a wrapped Response."""
        return await self.call.wrapped(ctx, *args, **kwargs)

    async def wrapped_stream(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncTrace[
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ]:
        """Stream the traced function and return a wrapped StreamResponse."""
        return await self.stream.wrapped(ctx, *args, **kwargs)
