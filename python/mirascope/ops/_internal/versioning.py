"""Versioning implementation for Mirascope ops."""

from __future__ import annotations

import logging
from collections.abc import Generator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, NewType, overload

from ..exceptions import ClosureComputationError
from .closure import Closure
from .protocols import AsyncFunction, SyncFunction, fn_is_async
from .spans import Span
from .traced_functions import (
    AsyncTrace,
    BaseAsyncTracedFunction,
    BaseSyncTracedFunction,
    Trace,
    _BaseTracedFunction,
    record_result_to_span,
)
from .types import P, R

logger = logging.getLogger(__name__)


VersionId = NewType("VersionId", str)
"""Unique identifier for a specific version."""

VersionRef = NewType("VersionRef", str)
"""Reference to a version (can be tag, hash, or semantic version)."""


# NOTE: the `.get_version` methods will need to do some type-hint magic to get the
# correct type-hints for the desired version (i.e. the input args and return type) since
# those are not necessarily the same as the current version. This is what we did in v0,
# so we'll just need to replicate that functionality here when we get there.


@dataclass(kw_only=True, frozen=True)
class VersionedResult(Trace[R]):
    """Per-call handle returned by `.wrapped()` methods for versioned functions.

    Provides access to the result and per-call operations for annotation,
    tagging, and assignment within a specific trace span context.
    """

    function_uuid: str | None = None


@dataclass(kw_only=True, frozen=True)
class AsyncVersionedResult(AsyncTrace[R]):
    """Per-call handle returned by async `.wrapped()` methods for versioned functions.

    Provides access to the result and per-call operations for annotation,
    tagging, and assignment within a specific trace span context.
    """

    function_uuid: str | None = None


@dataclass(kw_only=True, frozen=True)
class VersionInfo:
    """Static version metadata for a versioned function.

    Contains all information needed to identify and describe a specific version
    of a function, including its computed version number and hashes.
    """

    uuid: str | None
    """Server-assigned unique identifier for this version (None if not registered)."""

    hash: str
    """SHA256 hash of the complete closure code."""

    signature_hash: str
    """SHA256 hash of the function signature."""

    name: str
    """Display name for the versioned function."""

    description: str | None
    """Human-readable description of the versioned function."""

    version: str
    """Auto-computed semantic version in X.Y format."""

    tags: tuple[str, ...]
    """Tags associated with this version for filtering/classification."""

    metadata: Mapping[str, str]
    """Arbitrary key-value pairs for additional metadata."""

    # This will be covered in the next PR in this stack...
    def __post_init__(self) -> None:  # pragma: no cover
        """Clean up tags and initialize frozen metadata after dataclass init."""
        object.__setattr__(self, "tags", tuple(sorted(set(self.tags or []))))
        object.__setattr__(self, "metadata", dict(self.metadata))


@dataclass(kw_only=True)
class _BaseVersionedFunction(_BaseTracedFunction[P, R, Any]):
    """Base class for versioned functions."""

    name: str | None = None
    """Optional custom name for the versioned function (overrides function name)."""

    closure: Closure | None = field(init=False, default=None)
    """The closure of the versioned function."""

    def __post_init__(self) -> None:
        super().__post_init__()
        try:
            self.closure = Closure.from_fn(self.fn)
        except ClosureComputationError as e:
            logger.warning(
                "Failed to build closure for %s; continuing without version registration: %s",
                e.qualified_name,
                e,
            )

    @contextmanager
    def _versioned_span(
        self, function_uuid: str | None, *args: P.args, **kwargs: P.kwargs
    ) -> Generator[Span, None, None]:
        with super()._span(*args, **kwargs) as span:
            if self.closure is not None:
                span.set(function_hash=self.closure.hash)
                if self.closure.docstring:
                    span.set(
                        **{"mirascope.version.description": self.closure.docstring}
                    )
            if function_uuid:
                span.set(function_uuid=function_uuid)
            if self.name:
                span.set(**{"mirascope.version.name": self.name})
            yield span


@dataclass(kw_only=True)
class VersionedFunction(_BaseVersionedFunction[P, R], BaseSyncTracedFunction[P, R]):
    """Wrapper for synchronous functions with versioning capabilities."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Returns the result of the versioned function directly.

        A new version will be created if none yet exists for the specific version of
        this function that's being run.
        """
        function_uuid = self._ensure_registration()
        with self._versioned_span(function_uuid, *args, **kwargs) as span:
            result = self.fn(*args, **kwargs)
            record_result_to_span(span, result)
            return result

    def wrapped(self, *args: P.args, **kwargs: P.kwargs) -> VersionedResult[R]:
        """Return a wrapper around the executed function's result for trace utilities.

        Args:
            *args: Positional arguments for the wrapped function.
            **kwargs: Keyword arguments including 'version' for version reference.

        Returns:
            A VersionedResult containing the function result and trace context.
        """
        function_uuid = self._ensure_registration()
        with self._versioned_span(function_uuid, *args, **kwargs) as span:
            result = self.fn(*args, **kwargs)
            record_result_to_span(span, result)
            return VersionedResult(
                result=result,
                span=span,
                function_uuid=function_uuid,
            )

    def get_version(self, version: VersionId) -> VersionedFunction[P, R]:
        """Returns the specific version of this function requested."""
        raise NotImplementedError("VersionedFunction.get_version not yet implemented")

    def _ensure_registration(self) -> str | None:
        """Returns function UUID after ensuring registration with API.

        TODO: Implement API client integration to:
        1. Get sync client via `get_sync_client()`
        2. Check if function exists by hash: `client.functions.get_function_by_hash(self.closure.hash)`
        3. If not found, create new version: `client.functions.create_a_new_function_version(...)`
        4. Return the function UUID

        Example implementation (from lilypad):
        ```python
        if self.closure is None:
            return None
        try:
            client = get_sync_client()
        except Exception as e:
            logger.warning(f"Failed to get client for function registration: {e}")
            return None

        try:
            existing = client.functions.get_function_by_hash(self.closure.hash)
            return existing.uuid_
        except NotFoundError:
            response = client.functions.create_a_new_function_version(
                code=self.closure.code,
                hash=self.closure.hash,
                name=self.closure.name,
                signature=self.closure.signature,
                dependencies=self.closure.dependencies,
            )
            return response.uuid_
        ```
        """
        # TODO: Implement when API client is available
        return None


@dataclass(kw_only=True)
class AsyncVersionedFunction(
    _BaseVersionedFunction[P, R], BaseAsyncTracedFunction[P, R]
):
    """Wrapper for asynchronous functions with versioning capabilities."""

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Returns the result of the versioned function directly."""
        function_uuid = await self._ensure_registration()
        with self._versioned_span(function_uuid, *args, **kwargs) as span:
            result = await self.fn(*args, **kwargs)
            record_result_to_span(span, result)
            return result

    async def wrapped(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncVersionedResult[R]:
        """Returns a wrapper around the traced function's result for trace utilities."""
        function_uuid = await self._ensure_registration()
        with self._versioned_span(function_uuid, *args, **kwargs) as span:
            result = await self.fn(*args, **kwargs)
            record_result_to_span(span, result)
            return AsyncVersionedResult(
                result=result,
                span=span,
                function_uuid=function_uuid,
            )

    async def get_version(self, version: VersionId) -> VersionedFunction[P, R]:
        """Returns the specific version of this function using an `AsyncLilypad` client."""
        raise NotImplementedError(
            "AsyncVersionedFunction.get_version not yet implemented"
        )

    async def _ensure_registration(self) -> str | None:
        """Returns function UUID after ensuring registration with API.

        TODO: Implement API client integration to:
        1. Get async client via `get_async_client()`
        2. Check if function exists by hash: `await client.functions.get_function_by_hash(self.closure.hash)`
        3. If not found, create new version: `await client.functions.create_a_new_function_version(...)`
        4. Return the function UUID

        Example implementation (from lilypad):
        ```python
        if self.closure is None:
            return None
        try:
            client = get_async_client()
        except Exception as e:
            logger.warning(f"Failed to get client for function registration: {e}")
            return None

        try:
            existing = await client.functions.get_function_by_hash(self.closure.hash)
            return existing.uuid_
        except NotFoundError:
            response = await client.functions.create_a_new_function_version(
                code=self.closure.code,
                hash=self.closure.hash,
                name=self.closure.name,
                signature=self.closure.signature,
                dependencies=self.closure.dependencies,
            )
            return response.uuid_
        ```
        """
        # TODO: Implement when API client is available
        return None


@dataclass(kw_only=True)
class VersionDecorator:
    """Decorator implementation for adding versioning capabilities to functions."""

    tags: tuple[str, ...] = ()
    """Tags to be associated with versioned function calls."""

    name: str | None = None
    """Optional custom name for the versioned function."""

    description: str | None = None
    """Human-readable description of the versioned function."""

    metadata: dict[str, str] = field(default_factory=dict)
    """Arbitrary key-value pairs for additional metadata."""

    @overload
    def __call__(  # pyright: ignore[reportOverlappingOverload]
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
        """Overload for applying decorator to an async function."""
        ...

    def __call__(
        self,
        fn: SyncFunction[P, R] | AsyncFunction[P, R],
    ) -> VersionedFunction[P, R] | AsyncVersionedFunction[P, R]:
        """Applies the decorator to the given function."""
        if fn_is_async(fn):
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


def version(
    __fn: SyncFunction[P, R] | AsyncFunction[P, R] | None = None,
    *,
    tags: Sequence[str] | None = None,
    name: str | None = None,
    metadata: dict[str, str] | None = None,
) -> VersionDecorator | VersionedFunction[P, R] | AsyncVersionedFunction[P, R]:
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
    if __fn:
        if fn_is_async(__fn):
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
    else:
        return VersionDecorator(
            tags=tags,
            name=name,
            metadata=metadata,
        )
