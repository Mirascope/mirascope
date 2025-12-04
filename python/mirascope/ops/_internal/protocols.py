"""Call protocol helpers for ops.tracing."""

from __future__ import annotations

import inspect
from typing import Protocol
from typing_extensions import TypeIs

from ...llm.context import Context, DepsT
from .types import P, R


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
