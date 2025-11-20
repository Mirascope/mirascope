"""Tracing decorators for `mirascope.ops`."""

from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import (
    Any,
    Generic,
    Literal,
    TypeAlias,
    TypeVar,
    overload,
)

from .protocols import AsyncFunction, SyncFunction, fn_is_async
from .spans import Span
from .types import Jsonable, P, R
from .utils import get_qualified_name, json_dumps

FunctionT = TypeVar("FunctionT", bound="SyncFunction | AsyncFunction", covariant=True)

PrimitiveType: TypeAlias = str | int | float | bool


@dataclass(kw_only=True, frozen=True)
class _BaseTracedResult(Generic[R]):
    """Base class for traced results with shared functionality."""

    result: R
    """Return value produced by the traced call."""

    span: Span
    """Span associated with the traced call."""

    @property
    def span_id(self) -> str | None:
        """Returns the ID of the span for the traced result."""
        return self.span.span_id

    @property
    def trace_id(self) -> str | None:
        """Returns the ID of the trace for the traced result."""
        return self.span.trace_id


@dataclass(kw_only=True, frozen=True)
class TracedResult(_BaseTracedResult[R]):
    """Per-call handle returned by sync `.wrapped()` methods.

    Provides access to the result and per-call operations for annotation,
    tagging, and assignment within a specific trace span context.
    """

    def annotate(
        self,
        *,
        label: Literal["pass", "fail"],
        reasoning: str | None = None,
        metadata: dict[str, Jsonable] | None = None,
    ) -> None:
        """Annotates the current trace span."""
        raise NotImplementedError("TraceResult.annotate not yet implemented")

    def tag(self, *tags: str) -> None:
        """Adds given tags to the current trace span."""
        raise NotImplementedError("TraceResult.tag not yet implemented")

    def assign(self, *emails: str) -> None:
        """Assigns the trace to users with the given emails."""
        raise NotImplementedError("TraceResult.assign not yet implemented")


@dataclass(kw_only=True, frozen=True)
class AsyncTracedResult(_BaseTracedResult[R]):
    """Per-call handle returned by async `.wrapped()` methods.

    Provides access to the result and per-call operations for annotation,
    tagging, and assignment within a specific trace span context.
    """

    async def annotate(
        self,
        *,
        label: str | None = None,
        data: dict[str, Jsonable] | None = None,
        reasoning: str | None = None,
    ) -> None:
        """Annotates the current trace span."""
        raise NotImplementedError("AsyncTraceResult.annotate not yet implemented")

    async def tag(self, *tags: str) -> None:
        """Adds given tags to the current trace span."""
        raise NotImplementedError("AsyncTraceResult.tag not yet implemented")

    async def assign(self, *emails: str) -> None:
        """Assigns the trace to users with the given emails."""
        raise NotImplementedError("AsyncTraceResult.assign not yet implemented")


@dataclass(kw_only=True)
class _BaseTracedFunction(Generic[P, R, FunctionT], ABC):
    """Abstract base class for traced function wrappers."""

    fn: FunctionT
    """The function being traced."""

    tags: tuple[str, ...]
    """Tags to be associated with the trace span."""

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

    def _extract_arguments(
        self,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> tuple[dict[str, str], dict[str, Any]]:
        """Returns a tuple of (arg_types, arg_values) dictionaries from function call."""
        signature = inspect.signature(self.fn)
        bound_arguments = signature.bind(*args, **kwargs)
        bound_arguments.apply_defaults()

        arg_types = {}
        arg_values = {}

        for param_name, param_value in bound_arguments.arguments.items():
            parameter = signature.parameters[param_name]
            if parameter.annotation != inspect.Parameter.empty:
                if hasattr(parameter.annotation, "__name__"):
                    type_str = parameter.annotation.__name__
                else:
                    type_str = str(parameter.annotation)
                arg_types[param_name] = type_str
            else:
                arg_types[param_name] = type(param_value).__name__

            if isinstance(param_value, PrimitiveType) or param_value is None:
                arg_values[param_name] = param_value
            else:
                try:
                    json_dumps(param_value)
                    arg_values[param_name] = param_value
                except (TypeError, ValueError):
                    arg_values[param_name] = repr(param_value)

        return arg_types, arg_values

    @contextmanager
    def _span(self, *args: P.args, **kwargs: P.kwargs) -> Generator[Span, None, None]:
        """Returns a span context manager populated with call attributes."""
        arg_types, arg_values = self._extract_arguments(*args, **kwargs)
        with Span(self._qualified_name) as span:
            attributes = {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": self._qualified_name,
                "mirascope.fn.module": self._module_name,
                "mirascope.fn.is_async": self._is_async,
                "mirascope.trace.arg_types": json_dumps(arg_types),
                "mirascope.trace.arg_values": json_dumps(arg_values),
            }
            if self.tags:
                attributes["mirascope.trace.tags"] = self.tags
            span.set(**attributes)
            yield span

    def _record_result(self, span: Span, result: R) -> None:
        """Records the function result in the given span."""
        if result is None:
            return  # NOTE: we treat `None` valued results as such through omission.
        elif isinstance(result, PrimitiveType):
            output = result
        else:
            try:
                output = json_dumps(result)
            except (TypeError, ValueError):
                output = repr(result)
        span.set(**{"mirascope.trace.output": output})


@dataclass(kw_only=True)
class BaseSyncTracedFunction(_BaseTracedFunction[P, R, SyncFunction[P, R]]):
    """Abstract base class for synchronous traced function wrappers."""

    _is_async: bool = field(default=False, init=False)
    """Whether the wrapped function is asynchronous."""

    @abstractmethod
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Returns the result of the traced function."""
        ...

    @abstractmethod
    def wrapped(self, *args: P.args, **kwargs: P.kwargs) -> TracedResult[R]:
        """Returns a wrapper around the traced function's result for trace utilities."""
        ...


@dataclass(kw_only=True)
class TracedFunction(BaseSyncTracedFunction[P, R]):
    """Wrapper for synchronous functions with tracing capabilities.

    Provides both direct call and wrapped call methods for traced execution
    of synchronous functions.
    """

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Returns the result of the traced function."""
        with self._span(*args, **kwargs) as span:
            result = self.fn(*args, **kwargs)
            self._record_result(span, result)
            return result

    def wrapped(self, *args: P.args, **kwargs: P.kwargs) -> TracedResult[R]:
        """Returns a wrapper around the traced function's result for trace utilities."""
        with self._span(*args, **kwargs) as span:
            result = self.fn(*args, **kwargs)
            self._record_result(span, result)
            return TracedResult(result=result, span=span)


@dataclass(kw_only=True)
class BaseAsyncTracedFunction(_BaseTracedFunction[P, R, AsyncFunction[P, R]]):
    """Abstract base class for asynchronous traced function wrappers."""

    _is_async: bool = field(default=True, init=False)
    """Whether the wrapped function is asynchronous."""

    @abstractmethod
    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Returns the result of the traced function."""
        ...

    @abstractmethod
    async def wrapped(self, *args: P.args, **kwargs: P.kwargs) -> AsyncTracedResult[R]:
        """Returns a wrapper around the traced function's result for trace utilities."""
        ...


@dataclass(kw_only=True)
class AsyncTracedFunction(BaseAsyncTracedFunction[P, R]):
    """Wrapper for asynchronous functions with tracing capabilities.

    Provides both direct call and wrapped call methods for traced execution
    of asynchronous functions.
    """

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Returns the result of the traced function."""
        with self._span(*args, **kwargs) as span:
            result = await self.fn(*args, **kwargs)
            self._record_result(span, result)
            return result

    async def wrapped(self, *args: P.args, **kwargs: P.kwargs) -> AsyncTracedResult[R]:
        """Returns a wrapper around the traced function's result for trace utilities."""
        with self._span(*args, **kwargs) as span:
            result = await self.fn(*args, **kwargs)
            self._record_result(span, result)
            return AsyncTracedResult(result=result, span=span)


@dataclass(kw_only=True)
class TraceDecorator:
    """Decorator implementation for adding tracing capabilities to functions."""

    tags: tuple[str, ...] = ()
    """Tags to be associated with traced function calls."""

    # IMPORTANT: The order of these overloads must be preserved.
    # Pyright requires the async overload to be declared first for proper type inference.
    # If the sync overload is placed before the async overload, pyright will fail to
    # correctly recognize async functions when using the @overload decorator.
    @overload
    def __call__(  # pyright: ignore[reportOverlappingOverload]
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

    def __call__(
        self,
        fn: SyncFunction[P, R] | AsyncFunction[P, R],
    ) -> TracedFunction[P, R] | AsyncTracedFunction[P, R]:
        """Applies the decorator to the given function."""
        if fn_is_async(fn):
            return AsyncTracedFunction(fn=fn, tags=self.tags)
        else:
            return TracedFunction(fn=fn, tags=self.tags)


@overload
def trace(__fn: None = None, *, tags: list[str] | None = None) -> TraceDecorator:
    """Overload for providing kwargs before decorating (e.g. tags)."""
    ...


@overload
def trace(__fn: AsyncFunction[P, R], *, tags: None = None) -> AsyncTracedFunction[P, R]:  # pyright: ignore[reportOverlappingOverload]
    """Overload for directly (no argument) decorating an asynchronous function"""
    ...


@overload
def trace(__fn: SyncFunction[P, R], *, tags: None = None) -> TracedFunction[P, R]:
    """Overload for directly (no argument) decorating a synchronous function"""
    ...


def trace(
    __fn: SyncFunction[P, R] | AsyncFunction[P, R] | None = None,
    *,
    tags: list[str] | None = None,
) -> TraceDecorator | TracedFunction[P, R] | AsyncTracedFunction[P, R]:
    """Decorator for adding tracing capabilities to functions.

    Creates a wrapper that enables distributed tracing, performance monitoring,
    and execution tracking for decorated functions.

    Args:
        __fn: The function to decorate.
        tags: Optional list of string tags to associate with traced executions.

    Returns:
        A decorator that wraps functions with tracing capabilities.

    Example:
        ```python
        @ops.trace()
        def process_data(data: dict) -> dict:
            return {"processed": data}
        ```

    Example:
        ```python
        @ops.trace(tags=["production", "critical"])
        async def fetch_user(user_id: int) -> User:
            return await get_user(user_id)
        ```
    """
    normalized_tags = tuple(sorted(set(tags or [])))
    if __fn:
        if fn_is_async(__fn):
            return AsyncTracedFunction(fn=__fn, tags=normalized_tags)
        else:
            return TracedFunction(fn=__fn, tags=normalized_tags)
    else:
        return TraceDecorator(tags=normalized_tags)
