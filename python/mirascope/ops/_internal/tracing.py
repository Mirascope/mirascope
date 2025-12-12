from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    overload,
)

from ...llm.calls import AsyncCall, AsyncContextCall, Call, ContextCall
from ...llm.context import DepsT
from .protocols import (
    AsyncFunction,
    SyncFunction,
    fn_is_async,
)
from .traced_calls import (
    TracedAsyncCall,
    TracedAsyncContextCall,
    TracedCall,
    TracedContextCall,
    is_call_type,
    wrap_call,
)
from .traced_functions import (
    AsyncTracedFunction,
    TracedFunction,
)
from .types import P, R

if TYPE_CHECKING:
    from ...llm.formatting import FormattableT


@dataclass(kw_only=True)
class TraceDecorator:
    """Decorator implementation for adding tracing capabilities to functions."""

    tags: tuple[str, ...] = ()
    """Tags to be associated with traced function calls."""

    metadata: dict[str, str] = field(default_factory=dict)
    """Arbitrary key-value pairs for additional metadata."""

    # IMPORTANT: The order of these overloads matters for type inference.
    # Call type overloads come first, then function overloads.
    @overload
    def __call__(  # pyright: ignore[reportOverlappingOverload]
        self,
        fn: AsyncContextCall[P, DepsT, FormattableT],
    ) -> TracedAsyncContextCall[P, DepsT, FormattableT]:
        """Overload for applying decorator to an AsyncContextCall."""
        ...

    @overload
    def __call__(
        self,
        fn: ContextCall[P, DepsT, FormattableT],
    ) -> TracedContextCall[P, DepsT, FormattableT]:
        """Overload for applying decorator to a ContextCall."""
        ...

    @overload
    def __call__(
        self,
        fn: AsyncCall[P, FormattableT],
    ) -> TracedAsyncCall[P, FormattableT]:
        """Overload for applying decorator to an AsyncCall."""
        ...

    @overload
    def __call__(
        self,
        fn: Call[P, FormattableT],
    ) -> TracedCall[P, FormattableT]:
        """Overload for applying decorator to a Call."""
        ...

    @overload
    def __call__(
        self,
        fn: AsyncFunction[P, R],
    ) -> AsyncTracedFunction[P, R]:
        """Overload for applying decorator to an async function."""
        ...

    @overload
    def __call__(
        self,
        fn: SyncFunction[P, R],
    ) -> TracedFunction[P, R]:
        """Overload for applying decorator to a sync function."""
        ...

    def __call__(  # pyright: ignore[reportGeneralTypeIssues]
        self,
        fn: (
            AsyncContextCall[P, DepsT, FormattableT]
            | ContextCall[P, DepsT, FormattableT]
            | AsyncCall[P, FormattableT]
            | Call[P, FormattableT]
            | AsyncFunction[P, R]
            | SyncFunction[P, R]
        ),
    ) -> (
        TracedAsyncContextCall[P, DepsT, FormattableT]
        | TracedContextCall[P, DepsT, FormattableT]
        | TracedAsyncCall[P, FormattableT]
        | TracedCall[P, FormattableT]
        | AsyncTracedFunction[P, R]
        | TracedFunction[P, R]
    ):
        """Applies the decorator to the given function or Call object."""
        if is_call_type(fn):
            return wrap_call(fn=fn, tags=self.tags, metadata=self.metadata)
        elif fn_is_async(fn):
            return AsyncTracedFunction(fn=fn, tags=self.tags, metadata=self.metadata)
        else:
            return TracedFunction(fn=fn, tags=self.tags, metadata=self.metadata)


@overload
def trace(
    __fn: None = None,
    *,
    tags: list[str] | None = None,
    metadata: dict[str, str] | None = None,
) -> TraceDecorator:
    """Overload for providing kwargs before decorating (e.g. tags)."""
    ...


@overload
def trace(  # pyright: ignore[reportOverlappingOverload]
    __fn: AsyncContextCall[P, DepsT, FormattableT],
    *,
    tags: None = None,
    metadata: None = None,
) -> TracedAsyncContextCall[P, DepsT, FormattableT]:
    """Overload for directly decorating an AsyncContextCall."""
    ...


@overload
def trace(
    __fn: ContextCall[P, DepsT, FormattableT],
    *,
    tags: None = None,
    metadata: None = None,
) -> TracedContextCall[P, DepsT, FormattableT]:
    """Overload for directly decorating a ContextCall."""
    ...


@overload
def trace(
    __fn: AsyncCall[P, FormattableT],
    *,
    tags: None = None,
    metadata: None = None,
) -> TracedAsyncCall[P, FormattableT]:
    """Overload for directly decorating an AsyncCall."""
    ...


@overload
def trace(
    __fn: Call[P, FormattableT],
    *,
    tags: None = None,
    metadata: None = None,
) -> TracedCall[P, FormattableT]:
    """Overload for directly decorating a Call."""
    ...


@overload
def trace(
    __fn: AsyncFunction[P, R],
    *,
    tags: None = None,
    metadata: None = None,
) -> AsyncTracedFunction[P, R]:
    """Overload for directly (no argument) decorating an asynchronous function"""
    ...


@overload
def trace(
    __fn: SyncFunction[P, R],
    *,
    tags: None = None,
    metadata: None = None,
) -> TracedFunction[P, R]:
    """Overload for directly (no argument) decorating a synchronous function"""
    ...


def trace(  # pyright: ignore[reportGeneralTypeIssues]
    __fn: (
        AsyncContextCall[P, DepsT, FormattableT]
        | ContextCall[P, DepsT, FormattableT]
        | AsyncCall[P, FormattableT]
        | Call[P, FormattableT]
        | AsyncFunction[P, R]
        | SyncFunction[P, R]
        | None
    ) = None,
    *,
    tags: Sequence[str] | None = None,
    metadata: dict[str, str] | None = None,
) -> (
    TracedAsyncContextCall[P, DepsT, FormattableT]
    | TracedContextCall[P, DepsT, FormattableT]
    | TracedAsyncCall[P, FormattableT]
    | TracedCall[P, FormattableT]
    | AsyncTracedFunction[P, R]
    | TracedFunction[P, R]
    | TraceDecorator
):
    """Decorator for adding tracing capabilities to functions and LLM calls.

    Creates a wrapper that enables distributed tracing, performance monitoring,
    and execution tracking for decorated functions. When called, the decorated
    function returns a Trace containing both the result and span info.

    When decorating an @llm.call function, returns a TracedCall that wraps both
    the call and stream methods with tracing capabilities.

    Args:
        __fn: The function or Call object to decorate.
        tags: Optional list of string tags to associate with traced executions.
        metadata: Arbitrary key-value pairs for additional metadata.

    Returns:
        A decorator that wraps functions with tracing capabilities.

    Example:
        ```python
        @ops.trace
        def process_data(data: dict) -> dict:
            return {"processed": data}

        traced_result = process_data({"key": "value"})
        print(traced_result.result)    # {"processed": {"key": "value"}}
        print(traced_result.span_id)   # Access span ID
        ```

    Example:
        ```python
        @ops.trace
        @llm.call("gpt-4o-mini")
        def recommend_book(genre: str):
            return f"Recommend a {genre} book"

        # Returns Response directly (execution is still traced)
        response = recommend_book("fantasy")
        print(response.content)

        # Use .wrapped() to get Trace[Response] with span info
        trace = recommend_book.wrapped("fantasy")
        print(trace.result.content)
        print(trace.span_id)
        ```
    """
    tags = tuple(sorted(set(tags or [])))
    metadata = metadata or {}
    if __fn is None:
        return TraceDecorator(tags=tags, metadata=metadata)

    if is_call_type(__fn):
        return wrap_call(fn=__fn, tags=tags, metadata=metadata)
    elif fn_is_async(__fn):
        return AsyncTracedFunction(fn=__fn, tags=tags, metadata=metadata)
    else:
        return TracedFunction(fn=__fn, tags=tags, metadata=metadata)
