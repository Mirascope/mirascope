"""Tracing decorators for `mirascope.ops`."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import (
    Any,
    Generic,
    Literal,
    TypeVar,
)

from opentelemetry.util.types import AttributeValue

from ...llm.context import Context, DepsT
from ...llm.responses.root_response import RootResponse
from .protocols import (
    AsyncContextFunction,
    AsyncFunction,
    SyncContextFunction,
    SyncFunction,
)
from .spans import Span
from .types import Jsonable, P, R
from .utils import PrimitiveType, extract_arguments, get_qualified_name, json_dumps

FunctionT = TypeVar(
    "FunctionT",
    bound="SyncFunction[..., Any] | AsyncFunction[..., Any]",
    covariant=True,
)


def record_result_to_span(span: Span, result: object) -> None:
    """Records the function result in the given span.

    This is a shared helper function used by all traced function classes
    to record results consistently.
    """
    if result is None:
        return  # NOTE: we treat `None` valued results as such through omission.
    elif isinstance(result, PrimitiveType):
        output: str | int | float | bool = result
    elif isinstance(result, RootResponse):
        output = result.pretty()
    else:
        try:
            output = json_dumps(result)
        except (TypeError, ValueError):
            output = repr(result)
    span.set(**{"mirascope.trace.output": output})


@dataclass(kw_only=True, frozen=True)
class _BaseTrace(Generic[R]):
    """Base class for trace results with shared functionality."""

    result: R
    """Return value produced by the traced call."""

    span: Span
    """Span associated with the traced call."""

    @property
    def span_id(self) -> str | None:
        """Returns the ID of the span for the trace."""
        return self.span.span_id

    @property
    def trace_id(self) -> str | None:
        """Returns the ID of the trace."""
        return self.span.trace_id


@dataclass(kw_only=True, frozen=True)
class Trace(_BaseTrace[R]):
    """Result container returned by traced function calls.

    Provides access to the function result and trace span metadata,
    as well as per-call operations for annotation, tagging, and assignment.
    """

    def annotate(
        self,
        *,
        label: Literal["pass", "fail"],
        reasoning: str | None = None,
        metadata: dict[str, Jsonable] | None = None,
    ) -> None:
        """Annotates the current trace span."""
        raise NotImplementedError("Trace.annotate not yet implemented")

    def tag(self, *tags: str) -> None:
        """Adds given tags to the current trace span."""
        raise NotImplementedError("Trace.tag not yet implemented")

    def assign(self, *emails: str) -> None:
        """Assigns the trace to users with the given emails."""
        raise NotImplementedError("Trace.assign not yet implemented")


@dataclass(kw_only=True, frozen=True)
class AsyncTrace(_BaseTrace[R]):
    """Result container returned by async traced function calls.

    Provides access to the function result and trace span metadata,
    as well as per-call operations for annotation, tagging, and assignment.
    """

    async def annotate(
        self,
        *,
        label: str | None = None,
        data: dict[str, Jsonable] | None = None,
        reasoning: str | None = None,
    ) -> None:
        """Annotates the current trace span."""
        raise NotImplementedError("AsyncTrace.annotate not yet implemented")

    async def tag(self, *tags: str) -> None:
        """Adds given tags to the current trace span."""
        raise NotImplementedError("AsyncTrace.tag not yet implemented")

    async def assign(self, *emails: str) -> None:
        """Assigns the trace to users with the given emails."""
        raise NotImplementedError("AsyncTrace.assign not yet implemented")


@dataclass(kw_only=True)
class _BaseFunction(Generic[P, R, FunctionT], ABC):
    """Abstract base class for base functions to be traced."""

    fn: FunctionT
    """The function being traced."""

    tags: tuple[str, ...]
    """Tags to be associated with the trace span."""

    metadata: dict[str, str] = field(default_factory=dict)
    """Arbitrary key-value pairs for additional metadata."""

    _qualified_name: str = field(init=False)
    """Fully qualified name of the wrapped function."""

    _module_name: str = field(init=False)
    """Module name of the wrapped function."""

    _is_async: bool = field(init=False)
    """Whether the wrapped function is asynchronous."""

    def __post_init__(self) -> None:
        """Initialize additional attributes after dataclass init."""
        self._qualified_name = get_qualified_name(self.fn)
        self._module_name = getattr(self.fn, "__module__", "")


@dataclass(kw_only=True)
class _BaseTracedFunction(_BaseFunction[P, R, FunctionT]):
    """Abstract base class for traced function wrappers."""

    @contextmanager
    def _span(self, *args: P.args, **kwargs: P.kwargs) -> Generator[Span, None, None]:
        """Returns a span context manager populated with call attributes."""
        arg_types, arg_values = extract_arguments(self.fn, *args, **kwargs)
        with Span(self._qualified_name) as span:
            attributes: dict[str, AttributeValue] = {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": self._qualified_name,
                "mirascope.fn.module": self._module_name,
                "mirascope.fn.is_async": self._is_async,
                "mirascope.trace.arg_types": json_dumps(arg_types),
                "mirascope.trace.arg_values": json_dumps(arg_values),
            }
            if self.tags:
                attributes["mirascope.trace.tags"] = self.tags
            if self.metadata:
                attributes["mirascope.trace.metadata"] = json_dumps(self.metadata)
            span.set(**attributes)
            yield span


@dataclass(kw_only=True)
class BaseSyncTracedFunction(_BaseTracedFunction[P, R, SyncFunction[P, R]]):
    """Abstract base class for synchronous traced function wrappers."""

    _is_async: bool = field(default=False, init=False)
    """Whether the wrapped function is asynchronous."""

    @abstractmethod
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Returns the result of the traced function directly."""
        ...

    @abstractmethod
    def wrapped(self, *args: P.args, **kwargs: P.kwargs) -> Trace[R]:
        """Returns the trace containing the function result and span info."""
        ...


@dataclass(kw_only=True)
class TracedFunction(BaseSyncTracedFunction[P, R]):
    """Wrapper for synchronous functions with tracing capabilities.

    Provides traced execution of synchronous functions, returning Trace
    with access to span information.
    """

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Returns the result of the traced function directly."""
        with self._span(*args, **kwargs) as span:
            result = self.fn(*args, **kwargs)
            record_result_to_span(span, result)
            return result

    def wrapped(self, *args: P.args, **kwargs: P.kwargs) -> Trace[R]:
        """Returns the trace containing the function result and span info."""
        with self._span(*args, **kwargs) as span:
            result = self.fn(*args, **kwargs)
            record_result_to_span(span, result)
            return Trace(result=result, span=span)


@dataclass(kw_only=True)
class BaseAsyncTracedFunction(_BaseTracedFunction[P, R, AsyncFunction[P, R]]):
    """Abstract base class for asynchronous traced function wrappers."""

    _is_async: bool = field(default=True, init=False)
    """Whether the wrapped function is asynchronous."""

    @abstractmethod
    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Returns the result of the traced function directly."""
        ...

    @abstractmethod
    async def wrapped(self, *args: P.args, **kwargs: P.kwargs) -> AsyncTrace[R]:
        """Returns the trace containing the function result and span info."""
        ...


@dataclass(kw_only=True)
class AsyncTracedFunction(BaseAsyncTracedFunction[P, R]):
    """Wrapper for asynchronous functions with tracing capabilities.

    Provides traced execution of asynchronous functions, returning AsyncTrace
    with access to span information.
    """

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Returns the result of the traced function directly."""
        with self._span(*args, **kwargs) as span:
            result = await self.fn(*args, **kwargs)
            record_result_to_span(span, result)
            return result

    async def wrapped(self, *args: P.args, **kwargs: P.kwargs) -> AsyncTrace[R]:
        """Returns the trace containing the function result and span info."""
        with self._span(*args, **kwargs) as span:
            result = await self.fn(*args, **kwargs)
            record_result_to_span(span, result)
            return AsyncTrace(result=result, span=span)


@dataclass(kw_only=True)
class _BaseTracedContextFunction(
    _BaseFunction[P, R, FunctionT], Generic[P, DepsT, R, FunctionT]
):
    """Abstract base class for traced function wrappers."""

    _is_async: bool = field(default=False, init=False)
    """Whether the wrapped function is asynchronous."""

    @contextmanager
    def _span(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Generator[Span, None, None]:
        """Returns a span context manager populated with call attributes."""
        arg_types, arg_values = extract_arguments(self.fn, ctx, *args, **kwargs)
        with Span(name=self._qualified_name) as span:
            attributes: dict[str, AttributeValue] = {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": self._qualified_name,
                "mirascope.fn.module": self.fn.__module__,
                "mirascope.fn.is_async": self._is_async,
                "mirascope.trace.arg_types": json_dumps(arg_types),
                "mirascope.trace.arg_values": json_dumps(arg_values),
            }
            if self.tags:
                attributes["mirascope.trace.tags"] = self.tags
            if self.metadata:
                attributes["mirascope.trace.metadata"] = json_dumps(self.metadata)
            span.set(**attributes)
            yield span


@dataclass(kw_only=True)
class BaseTracedSyncContextFunction(
    _BaseTracedContextFunction[P, DepsT, R, SyncContextFunction[P, DepsT, R]]
):
    """Abstract base class for synchronous traced function wrappers."""

    _is_async: bool = field(default=False, init=False)
    """Whether the wrapped function is asynchronous."""

    @abstractmethod
    def __call__(self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs) -> R:
        """Returns the result of the traced function directly."""
        ...

    @abstractmethod
    def wrapped(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Trace[R]:
        """Returns the trace containing the function result and span info."""
        ...


@dataclass(kw_only=True)
class TracedContextFunction(BaseTracedSyncContextFunction[P, DepsT, R]):
    """Wrapper for synchronous context functions with tracing capabilities.

    Provides traced execution of synchronous functions that take a Context parameter,
    returning Trace with access to span information.
    """

    def __call__(self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs) -> R:
        """Returns the result of the traced function directly."""
        with self._span(ctx, *args, **kwargs) as span:
            result = self.fn(ctx, *args, **kwargs)
            record_result_to_span(span, result)
            return result

    def wrapped(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Trace[R]:
        """Returns the trace containing the function result and span info."""
        with self._span(ctx, *args, **kwargs) as span:
            result = self.fn(ctx, *args, **kwargs)
            record_result_to_span(span, result)
            return Trace(result=result, span=span)


@dataclass(kw_only=True)
class BaseTracedAsyncContextFunction(
    _BaseTracedContextFunction[P, DepsT, R, AsyncContextFunction[P, DepsT, R]]
):
    """Abstract base class for synchronous traced function wrappers."""

    _is_async: bool = field(default=True, init=False)
    """Whether the wrapped function is asynchronous."""

    @abstractmethod
    async def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> R:
        """Returns the result of the traced function directly."""
        ...

    @abstractmethod
    async def wrapped(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncTrace[R]:
        """Returns the trace containing the function result and span info."""
        ...


@dataclass(kw_only=True)
class AsyncTracedContextFunction(BaseTracedAsyncContextFunction[P, DepsT, R]):
    """Wrapper for asynchronous context functions with tracing capabilities.

    Provides traced execution of asynchronous functions that take a Context parameter,
    returning AsyncTrace with access to span information.
    """

    async def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> R:
        """Returns the result of the traced function directly."""
        with self._span(ctx, *args, **kwargs) as span:
            result = await self.fn(ctx, *args, **kwargs)
            record_result_to_span(span, result)
            return result

    async def wrapped(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncTrace[R]:
        """Returns the trace containing the function result and span info."""
        with self._span(ctx, *args, **kwargs) as span:
            result = await self.fn(ctx, *args, **kwargs)
            record_result_to_span(span, result)
            return AsyncTrace(result=result, span=span)
