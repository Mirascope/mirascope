"""Base classes for streaming content groups."""

from collections.abc import AsyncIterator, Iterator
from typing import Generic, TypeVar

from ..content import Content

ChunkT = TypeVar("ChunkT")
ContentT = TypeVar("ContentT", bound=Content)


class BaseGroup(Generic[ChunkT, ContentT]):
    """Base class for streaming content groups.
    
    Groups represent sequences of related chunks that accumulate into a final content object.
    They provide live-updating partial content and enforce sequential consumption.
    """

    @property
    def type(self) -> str:
        """The type identifier for this group."""
        raise NotImplementedError()

    @property
    def partial(self) -> ChunkT:
        """The latest accumulated chunk state, updated as chunks are consumed."""
        raise NotImplementedError()

    @property
    def final(self) -> ContentT | None:
        """The final content if the group is finished, None otherwise."""
        raise NotImplementedError()

    def __iter__(self) -> Iterator[ChunkT]:
        """Iterate through chunks in this group.
        
        Returns:
            Iterator yielding chunks
        """
        raise NotImplementedError()


class BaseAsyncGroup(Generic[ChunkT, ContentT]):
    """Base class for async streaming content groups.
    
    Async version of BaseGroup for asynchronous streaming.
    """

    @property
    def type(self) -> str:
        """The type identifier for this group."""
        raise NotImplementedError()

    @property
    def partial(self) -> ChunkT:
        """The latest accumulated chunk state, updated as chunks are consumed."""
        raise NotImplementedError()

    @property
    def final(self) -> ContentT | None:
        """The final content if the group is finished, None otherwise."""
        raise NotImplementedError()

    def __aiter__(self) -> AsyncIterator[ChunkT]:
        """Async iterate through chunks in this group.
        
        Returns:
            Async iterator yielding chunks
        """
        raise NotImplementedError()