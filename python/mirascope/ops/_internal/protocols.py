"""Call protocol helpers for ops.tracing."""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Protocol
from typing_extensions import TypeIs

from ...llm.context import Context, DepsT
from .types import P, R

if TYPE_CHECKING:
    from .spans import Span


class SyncFunction(Protocol[P, R]):
    """Protocol for synchronous callable functions."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """The function required a synchronous call method."""
        ...  # pragma: no cover


class AsyncFunction(Protocol[P, R]):
    """Protocol for asynchronous callable functions."""

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """The function's required asynchronous call method."""
        ...  # pragma: no cover


class SyncSpanFunction(Protocol[P, R]):
    """Protocol for synchronous functions that receive injected Span.

    Functions matching this protocol have `trace_ctx: Span` as their first
    parameter. The trace decorator will inject the span automatically.
    """

    def __call__(self, trace_ctx: Span, *args: P.args, **kwargs: P.kwargs) -> R:
        """The function receives a Span as first parameter."""
        ...  # pragma: no cover


class AsyncSpanFunction(Protocol[P, R]):
    """Protocol for asynchronous functions that receive injected Span.

    Functions matching this protocol have `trace_ctx: Span` as their first
    parameter. The trace decorator will inject the span automatically.
    """

    async def __call__(self, trace_ctx: Span, *args: P.args, **kwargs: P.kwargs) -> R:
        """The function receives a Span as first parameter."""
        ...  # pragma: no cover


class SyncContextFunction(Protocol[P, DepsT, R]):
    """Protocol for synchronous callable functions with Context parameter."""

    def __call__(self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs) -> R:
        """The function required a synchronous call method with context."""
        ...  # pragma: no cover


class AsyncContextFunction(Protocol[P, DepsT, R]):
    """Protocol for asynchronous callable functions with Context parameter."""

    async def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> R:
        """The function's required asynchronous call method with context."""
        ...  # pragma: no cover


def fn_is_async(
    fn: SyncFunction[P, R] | AsyncFunction[P, R],
) -> TypeIs[AsyncFunction[P, R]]:
    """Type check to determine if a given function is asynchronous."""
    return inspect.iscoroutinefunction(fn) or inspect.isasyncgenfunction(fn)


def fn_wants_span(
    fn: (
        SyncFunction[P, R]
        | AsyncFunction[P, R]
        | SyncSpanFunction[P, R]
        | AsyncSpanFunction[P, R]
    ),
) -> TypeIs[SyncSpanFunction[P, R] | AsyncSpanFunction[P, R]]:
    """Check if function wants Span injection as first parameter.

    Returns True if the function has a first parameter named `trace_ctx`
    with type annotation `Span`.
    """
    # Import here to avoid circular imports
    from .spans import Span

    try:
        sig = inspect.signature(fn)
    except (ValueError, TypeError):
        return False

    params = list(sig.parameters.values())
    if not params:
        return False

    first_param = params[0]
    if first_param.name != "trace_ctx":
        return False

    # Check annotation
    annotation = first_param.annotation
    if annotation is inspect.Parameter.empty:
        return False

    # Handle string annotations (forward references)
    # The annotation could be "Span", "ops.Span", "mirascope.ops.Span", etc.
    if isinstance(annotation, str):
        return annotation == "Span" or annotation.endswith(".Span")

    # Check by identity first
    if annotation is Span:
        return True

    # Fallback: check by class name and module for robustness
    # This handles cases where the same class might have different identities
    # due to module reloading or import issues in test environments
    if isinstance(annotation, type):
        return (
            annotation.__name__ == "Span"
            and annotation.__module__ == "mirascope.ops._internal.spans"
        )

    return False
