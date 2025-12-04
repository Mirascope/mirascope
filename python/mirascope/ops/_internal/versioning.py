"""Version decorator for Mirascope ops."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, overload

from ...llm.calls import AsyncCall, AsyncContextCall, Call, ContextCall
from ...llm.context import DepsT
from .protocols import AsyncFunction, SyncFunction, fn_is_async
from .types import P, R
from .versioned_calls import (
    VersionedAsyncCall,
    VersionedAsyncContextCall,
    VersionedCall,
    VersionedContextCall,
    is_version_call_type,
    wrap_version_call,
)
from .versioned_functions import AsyncVersionedFunction, VersionedFunction

if TYPE_CHECKING:
    from ...llm.formatting import FormattableT


@dataclass(kw_only=True)
class VersionDecorator:
    """Decorator implementation for adding versioning capabilities to functions."""

    tags: tuple[str, ...] = ()
    """Tags to be associated with versioned function calls."""

    name: str | None = None
    """Optional custom name for the versioned function."""

    metadata: dict[str, str] = field(default_factory=dict)
    """Arbitrary key-value pairs for additional metadata."""

    @overload
    def __call__(  # pyright: ignore[reportOverlappingOverload]
        self,
        fn: AsyncContextCall[P, DepsT, FormattableT],
    ) -> VersionedAsyncContextCall[P, DepsT, FormattableT]:
        """Overload for applying decorator to an AsyncContextCall."""
        ...

    @overload
    def __call__(
        self,
        fn: ContextCall[P, DepsT, FormattableT],
    ) -> VersionedContextCall[P, DepsT, FormattableT]:
        """Overload for applying decorator to a ContextCall."""
        ...

    @overload
    def __call__(
        self,
        fn: AsyncCall[P, FormattableT],
    ) -> VersionedAsyncCall[P, FormattableT]:
        """Overload for applying decorator to an AsyncCall."""
        ...

    @overload
    def __call__(
        self,
        fn: Call[P, FormattableT],
    ) -> VersionedCall[P, FormattableT]:
        """Overload for applying decorator to a Call."""
        ...

    @overload
    def __call__(
        self,
        fn: AsyncFunction[P, R],
    ) -> AsyncVersionedFunction[P, R]:
        """Overload for applying decorator to an async function."""
        ...

    @overload
    def __call__(
        self,
        fn: SyncFunction[P, R],
    ) -> VersionedFunction[P, R]:
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
        VersionedAsyncContextCall[P, DepsT, FormattableT]
        | VersionedContextCall[P, DepsT, FormattableT]
        | VersionedAsyncCall[P, FormattableT]
        | VersionedCall[P, FormattableT]
        | AsyncVersionedFunction[P, R]
        | VersionedFunction[P, R]
    ):
        """Applies the decorator to the given function or Call object."""
        if is_version_call_type(fn):
            return wrap_version_call(
                fn=fn,
                tags=self.tags,
                name=self.name,
                metadata=self.metadata or {},
            )
        elif fn_is_async(fn):
            return AsyncVersionedFunction(
                fn=fn,
                tags=self.tags,
                name=self.name,
                metadata=self.metadata,
            )
        else:
            return VersionedFunction(
                fn=fn,
                tags=self.tags,
                name=self.name,
                metadata=self.metadata,
            )


@overload
def version(
    __fn: None = None,
    *,
    tags: Sequence[str] | None = None,
    name: str | None = None,
    metadata: dict[str, str] | None = None,
) -> VersionDecorator:
    """Overload for providing kwargs before decorating (e.g. tags)."""
    ...


@overload
def version(  # pyright: ignore[reportOverlappingOverload]
    __fn: AsyncContextCall[P, DepsT, FormattableT],
    *,
    tags: None = None,
    name: None = None,
    metadata: None = None,
) -> VersionedAsyncContextCall[P, DepsT, FormattableT]:
    """Overload for directly (no argument) decorating an AsyncContextCall."""
    ...


@overload
def version(
    __fn: ContextCall[P, DepsT, FormattableT],
    *,
    tags: None = None,
    name: None = None,
    metadata: None = None,
) -> VersionedContextCall[P, DepsT, FormattableT]:
    """Overload for directly (no argument) decorating a ContextCall."""
    ...


@overload
def version(
    __fn: AsyncCall[P, FormattableT],
    *,
    tags: None = None,
    name: None = None,
    metadata: None = None,
) -> VersionedAsyncCall[P, FormattableT]:
    """Overload for directly (no argument) decorating an AsyncCall."""
    ...


@overload
def version(
    __fn: Call[P, FormattableT],
    *,
    tags: None = None,
    name: None = None,
    metadata: None = None,
) -> VersionedCall[P, FormattableT]:
    """Overload for directly (no argument) decorating a Call."""
    ...


@overload
def version(
    __fn: AsyncFunction[P, R],
    *,
    tags: None = None,
    name: None = None,
    metadata: None = None,
) -> AsyncVersionedFunction[P, R]:
    """Overload for directly (no argument) decorating an asynchronous function"""
    ...


@overload
def version(
    __fn: SyncFunction[P, R],
    *,
    tags: None = None,
    name: None = None,
    metadata: None = None,
) -> VersionedFunction[P, R]:
    """Overload for directly (no argument) decorating a synchronous function"""
    ...


def version(  # pyright: ignore[reportGeneralTypeIssues]
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
    name: str | None = None,
    metadata: dict[str, str] | None = None,
) -> (
    VersionDecorator
    | VersionedAsyncContextCall[P, DepsT, FormattableT]
    | VersionedContextCall[P, DepsT, FormattableT]
    | VersionedAsyncCall[P, FormattableT]
    | VersionedCall[P, FormattableT]
    | AsyncVersionedFunction[P, R]
    | VersionedFunction[P, R]
):
    """Add versioning capability to a callable function.

    Enables version management for functions, allowing execution of specific
    versions and version introspection. Can be composed with @trace and @remote.

    Args:
        __fn: The function to version (when used without parentheses).
        tags: Optional version tags for this function.
        name: Optional custom name for display (overrides function name).
        metadata: Arbitrary key-value pairs for additional metadata.

    Returns:
        A versioned callable or a decorator function.

    Examples:
        ```python
        @version()
        def compute(x: int) -> int:
            return x * 2
        ```

        ```python
        @version(tags=["v1.0"])
        async def process() -> str:
            return "processed"
        ```

        ```python
        @version(
            name="book_recommender",
            tags=["production"],
            metadata={"owner": "team-ml", "ticket": "ENG-1234"},
        )
        def recommend_book(genre: str) -> str:
            return f"Recommend a {genre} book"
        ```
    """
    tags = tuple(sorted(set(tags or [])))
    metadata = metadata or {}
    if __fn is None:
        return VersionDecorator(
            tags=tags,
            name=name,
            metadata=metadata,
        )

    if is_version_call_type(__fn):
        return wrap_version_call(
            fn=__fn,
            tags=tags,
            name=name,
            metadata=metadata,
        )
    elif fn_is_async(__fn):
        return AsyncVersionedFunction(
            fn=__fn,
            tags=tags,
            name=name,
            metadata=metadata,
        )
    else:
        return VersionedFunction(
            fn=__fn,
            tags=tags,
            name=name,
            metadata=metadata,
        )
