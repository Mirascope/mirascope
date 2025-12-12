"""Versioned call wrappers for @ops.version decorated @llm.call functions."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Concatenate, Generic
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
from ..exceptions import ClosureComputationError
from .closure import Closure
from .protocols import (
    AsyncFunction,
    R,
    SyncFunction,
)
from .versioned_functions import (
    AsyncVersionedFunction,
    AsyncVersionedResult,
    VersionedFunction,
    VersionedResult,
    VersionInfo,
    _BaseVersionedFunction,
)

logger = logging.getLogger(__name__)


def _compute_closure_from_call(
    call_obj: (
        ContextCall[P, DepsT, FormattableT]
        | AsyncContextCall[P, DepsT, FormattableT]
        | Call[P, FormattableT]
        | AsyncCall[P, FormattableT]
    ),
) -> Closure | None:
    """Compute closure from a Call object's prompt function.

    Extracts the original function from the Call's prompt closure and computes
    a Closure object for version tracking. Returns None if closure computation
    fails.
    """
    fn = call_obj.prompt.fn
    closure = getattr(fn, "__closure__", None)
    original_fn = closure[0].cell_contents if closure and len(closure) > 0 else fn
    try:
        return Closure.from_fn(original_fn)
    except ClosureComputationError as e:
        logger.warning(
            "Failed to build closure for %s; continuing without version registration: %s",
            e.qualified_name,
            e,
        )
        return None


def is_version_call_type(
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


def wrap_version_call(
    fn: (
        ContextCall[P, DepsT, FormattableT]
        | AsyncContextCall[P, DepsT, FormattableT]
        | Call[P, FormattableT]
        | AsyncCall[P, FormattableT]
    ),
    tags: tuple[str, ...],
    name: str | None,
    metadata: dict[str, str],
) -> (
    VersionedContextCall[P, DepsT, FormattableT]
    | VersionedAsyncContextCall[P, DepsT, FormattableT]
    | VersionedCall[P, FormattableT]
    | VersionedAsyncCall[P, FormattableT]
):
    """Wrap a Call object with the appropriate VersionedCall type."""
    if isinstance(fn, AsyncContextCall):
        return VersionedAsyncContextCall(
            _call=fn, tags=tags, name=name, metadata=metadata
        )
    elif isinstance(fn, ContextCall):
        return VersionedContextCall(_call=fn, tags=tags, name=name, metadata=metadata)
    elif isinstance(fn, AsyncCall):
        return VersionedAsyncCall(_call=fn, tags=tags, name=name, metadata=metadata)
    else:
        return VersionedCall(_call=fn, tags=tags, name=name, metadata=metadata)


@dataclass(kw_only=True)
class _BaseVersionedCall:
    """Base class for versioned call wrappers.

    Provides common fields and methods for all versioned call types,
    reducing code duplication across VersionedCall, VersionedAsyncCall,
    VersionedContextCall, and VersionedAsyncContextCall.
    """

    tags: tuple[str, ...]
    """Tags to be associated with versioned calls."""

    name: str | None = None
    """Optional custom name for the versioned function."""

    metadata: dict[str, str] = field(default_factory=dict)
    """Arbitrary key-value pairs for additional metadata."""

    closure: Closure | None = field(init=False, default=None)
    """Cached closure for the original function."""

    def _compute_closure(
        self,
        wrapped_call: (
            ContextCall[P, DepsT, FormattableT]
            | AsyncContextCall[P, DepsT, FormattableT]
            | Call[P, FormattableT]
            | AsyncCall[P, FormattableT]
        ),
        versioned_call: _BaseVersionedFunction[..., object],
        versioned_stream: _BaseVersionedFunction[..., object],
    ) -> None:
        """Initialize closure from wrapped call and assign to versioned wrappers."""
        self.closure = _compute_closure_from_call(wrapped_call)
        if self.closure is not None:
            versioned_call.closure = self.closure
            versioned_stream.closure = self.closure

    @property
    def version_info(self) -> VersionInfo | None:
        """Returns static version metadata for this versioned call."""
        if self.closure is None:
            return None
        return VersionInfo(
            uuid=None,
            hash=self.closure.hash,
            signature_hash=self.closure.signature_hash,
            name=self.name or self.closure.name,
            description=self.closure.docstring,
            version=_BaseVersionedFunction._compute_version(self.closure.hash),
            tags=self.tags,
            metadata=self.metadata,
        )


@dataclass(kw_only=True)
class VersionedCall(_BaseVersionedCall, Generic[P, FormattableT]):
    """Versioned wrapper for synchronous Call objects.

    When @ops.version decorates an @llm.call, it returns a VersionedCall that wraps
    the call and stream methods with versioning capabilities.

    Example:
        ```python
        @ops.version
        @llm.call("gpt-4o-mini")
        def recommend_book(genre: str):
            return f"Recommend a {genre} book"

        # Returns Response directly (but execution is versioned)
        response = recommend_book("fantasy")
        print(response.content)

        # Same as __call__
        response = recommend_book.call("fantasy")

        # Streaming returns StreamResponse (versioned)
        stream = recommend_book.stream("fantasy")
        for chunk in stream:
            print(chunk)

        # Use wrapped to get VersionedResult[Response] with version info
        result = recommend_book.wrapped("fantasy")
        print(result.result.content)
        print(result.function_uuid)

        # Use wrapped_stream to get VersionedResult[StreamResponse]
        result = recommend_book.wrapped_stream("fantasy")

        # Access version info
        info = recommend_book.version_info
        print(info.version, info.hash)
        ```
    """

    _call: Call[P, FormattableT]
    """The wrapped Call object."""

    call: VersionedFunction[P, Response | Response[FormattableT]] = field(init=False)
    """VersionedFunction wrapping the call method."""

    stream: VersionedFunction[P, StreamResponse | StreamResponse[FormattableT]] = field(
        init=False
    )
    """VersionedFunction wrapping the stream method."""

    def __post_init__(self) -> None:
        """Initialize VersionedFunction wrappers for call and stream methods."""
        self.call = VersionedFunction(
            fn=self._call.call,
            tags=self.tags,
            name=self.name,
            metadata=self.metadata,
        )
        self.stream = VersionedFunction(
            fn=self._call.stream,
            tags=self.tags,
            name=self.name,
            metadata=self.metadata,
        )
        self._compute_closure(self._call, self.call, self.stream)

    def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Response | Response[FormattableT]:
        """Call the versioned function and return Response directly."""
        return self.call(*args, **kwargs)

    def wrapped(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> VersionedResult[Response | Response[FormattableT]]:
        """Call the versioned function and return a wrapped Response."""
        return self.call.wrapped(*args, **kwargs)

    def wrapped_stream(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> VersionedResult[StreamResponse | StreamResponse[FormattableT]]:
        """Stream the versioned function and return a wrapped StreamResponse."""
        return self.stream.wrapped(*args, **kwargs)


@dataclass(kw_only=True)
class VersionedAsyncCall(_BaseVersionedCall, Generic[P, FormattableT]):
    """Versioned wrapper for asynchronous AsyncCall objects.

    Example:
        ```python
        @ops.version
        @llm.call("gpt-4o-mini")
        async def recommend_book(genre: str):
            return f"Recommend a {genre} book"

        # Returns AsyncResponse directly (but execution is versioned)
        response = await recommend_book("fantasy")
        print(response.content)

        # Use wrapped to get AsyncVersionedResult[AsyncResponse] with version info
        result = await recommend_book.wrapped("fantasy")
        print(result.result.content)
        print(result.function_uuid)
        ```
    """

    _call: AsyncCall[P, FormattableT]
    """The wrapped AsyncCall object."""

    call: AsyncVersionedFunction[P, AsyncResponse | AsyncResponse[FormattableT]] = (
        field(init=False)
    )
    """AsyncVersionedFunction wrapping the call method."""

    stream: AsyncVersionedFunction[
        P, AsyncStreamResponse | AsyncStreamResponse[FormattableT]
    ] = field(init=False)
    """AsyncVersionedFunction wrapping the stream method."""

    def __post_init__(self) -> None:
        """Initialize AsyncVersionedFunction wrappers for call and stream methods."""
        self.call = AsyncVersionedFunction(
            fn=self._call.call,
            tags=self.tags,
            name=self.name,
            metadata=self.metadata,
        )
        self.stream = AsyncVersionedFunction(
            fn=self._call.stream,
            tags=self.tags,
            name=self.name,
            metadata=self.metadata,
        )
        self._compute_closure(self._call, self.call, self.stream)

    async def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Call the versioned function and return AsyncResponse directly."""
        return await self.call(*args, **kwargs)

    async def wrapped(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncVersionedResult[AsyncResponse | AsyncResponse[FormattableT]]:
        """Call the versioned function and return a wrapped Response."""
        return await self.call.wrapped(*args, **kwargs)

    async def wrapped_stream(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncVersionedResult[AsyncStreamResponse | AsyncStreamResponse[FormattableT]]:
        """Stream the versioned function and return a wrapped StreamResponse."""
        return await self.stream.wrapped(*args, **kwargs)


@dataclass(kw_only=True)
class VersionedContextCall(_BaseVersionedCall, Generic[P, DepsT, FormattableT]):
    """Versioned wrapper for synchronous ContextCall objects.

    Example:
        ```python
        @ops.version
        @llm.call("gpt-4o-mini")
        def recommend_book(ctx: llm.Context[str], genre: str):
            return f"{ctx.deps} Recommend a {genre} book"

        ctx = llm.Context(deps="As a librarian,")

        # Returns ContextResponse directly (but execution is versioned)
        response = recommend_book(ctx, "fantasy")
        print(response.content)

        # Use wrapped to get VersionedResult[ContextResponse] with version info
        result = recommend_book.wrapped(ctx, "fantasy")
        print(result.result.content)
        ```
    """

    _call: ContextCall[P, DepsT, FormattableT]
    """The wrapped ContextCall object."""

    _call_versioned: VersionedFunction[
        Concatenate[Context[DepsT], P],
        ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT],
    ] = field(init=False)
    """VersionedFunction wrapping the call method."""

    _stream_versioned: VersionedFunction[
        Concatenate[Context[DepsT], P],
        ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT],
    ] = field(init=False)
    """VersionedFunction wrapping the stream method."""

    def __post_init__(self) -> None:
        """Initialize VersionedFunction wrappers for call and stream methods."""
        self._call_versioned = VersionedFunction(
            fn=self._call.call,
            tags=self.tags,
            name=self.name,
            metadata=self.metadata,
        )
        self._stream_versioned = VersionedFunction(
            fn=self._call.stream,
            tags=self.tags,
            name=self.name,
            metadata=self.metadata,
        )
        self._compute_closure(self._call, self._call_versioned, self._stream_versioned)

    def call(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Call the versioned function and return ContextResponse directly."""
        return self._call_versioned(ctx, *args, **kwargs)

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Call the versioned function and return ContextResponse directly."""
        return self.call(ctx, *args, **kwargs)

    def stream(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> (
        ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]
    ):
        """Stream the versioned function and return a ContextStreamResponse."""
        return self._stream_versioned(ctx, *args, **kwargs)

    def wrapped(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> VersionedResult[
        ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]
    ]:
        """Call the versioned function and return a wrapped Response."""
        return self._call_versioned.wrapped(ctx, *args, **kwargs)

    def wrapped_stream(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> VersionedResult[
        ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]
    ]:
        """Stream the versioned function and return a wrapped StreamResponse."""
        return self._stream_versioned.wrapped(ctx, *args, **kwargs)


@dataclass(kw_only=True)
class VersionedAsyncContextCall(_BaseVersionedCall, Generic[P, DepsT, FormattableT]):
    """Versioned wrapper for asynchronous AsyncContextCall objects.

    Example:
        ```python
        @ops.version
        @llm.call("gpt-4o-mini")
        async def recommend_book(ctx: llm.Context[str], genre: str):
            return f"{ctx.deps} Recommend a {genre} book"

        ctx = llm.Context(deps="As a librarian,")

        # Returns AsyncContextResponse directly (but execution is versioned)
        response = await recommend_book(ctx, "fantasy")
        print(response.content)

        # Use wrapped to get AsyncVersionedResult[AsyncContextResponse] with version info
        result = await recommend_book.wrapped(ctx, "fantasy")
        print(result.result.content)
        ```
    """

    _call: AsyncContextCall[P, DepsT, FormattableT]
    """The wrapped AsyncContextCall object."""

    _call_versioned: AsyncVersionedFunction[
        Concatenate[Context[DepsT], P],
        AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT],
    ] = field(init=False)
    """AsyncVersionedFunction wrapping the call method."""

    _stream_versioned: AsyncVersionedFunction[
        Concatenate[Context[DepsT], P],
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT],
    ] = field(init=False)
    """AsyncVersionedFunction wrapping the stream method."""

    def __post_init__(self) -> None:
        """Initialize AsyncVersionedFunction wrappers for call and stream methods."""
        self._call_versioned = AsyncVersionedFunction(
            fn=self._call.call,
            tags=self.tags,
            name=self.name,
            metadata=self.metadata,
        )
        self._stream_versioned = AsyncVersionedFunction(
            fn=self._call.stream,
            tags=self.tags,
            name=self.name,
            metadata=self.metadata,
        )
        self._compute_closure(self._call, self._call_versioned, self._stream_versioned)

    async def call(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Call the versioned function and return AsyncContextResponse directly."""
        return await self._call_versioned(ctx, *args, **kwargs)

    async def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Call the versioned function and return AsyncContextResponse directly."""
        return await self.call(ctx, *args, **kwargs)

    async def stream(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> (
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ):
        """Stream the versioned function and return an AsyncContextStreamResponse."""
        return await self._stream_versioned(ctx, *args, **kwargs)

    async def wrapped(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncVersionedResult[
        AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]
    ]:
        """Call the versioned function and return a wrapped Response."""
        return await self._call_versioned.wrapped(ctx, *args, **kwargs)

    async def wrapped_stream(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncVersionedResult[
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ]:
        """Stream the versioned function and return a wrapped StreamResponse."""
        return await self._stream_versioned.wrapped(ctx, *args, **kwargs)
