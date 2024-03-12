"""A base abstract interface for calling LLMs."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    Any,
    AsyncGenerator,
    ClassVar,
    Generator,
    Generic,
    Optional,
    TypeVar,
)

from .prompts import BasePrompt
from .types import BaseCallParams, BaseCallResponse, BaseCallResponseChunk

BaseCallResponseT = TypeVar("BaseCallResponseT", bound=BaseCallResponse)
BaseCallResponseChunkT = TypeVar("BaseCallResponseChunkT", bound=BaseCallResponseChunk)


class BaseCall(BasePrompt, Generic[BaseCallResponseT, BaseCallResponseChunkT], ABC):
    """The base class abstract interface for calling LLMs."""

    api_key: Optional[str] = None
    base_url: Optional[str] = None

    call_params: ClassVar[BaseCallParams]

    @abstractmethod
    def call(self, **kwargs: Any) -> BaseCallResponseT:
        """A call to an LLM.

        An implementation of this function must return a response that extends
        `BaseCallResponse`. This ensures a consistent API and convenience across e.g.
        different model providers.
        """
        ...  # pragma: no cover

    @abstractmethod
    async def call_async(self, **kwargs: Any) -> BaseCallResponseT:
        """An asynchronous call to an LLM.

        An implementation of this function must return a response that extends
        `BaseCallResponse`. This ensures a consistent API and convenience across e.g.
        different model providers.
        """
        ...  # pragma: no cover

    @abstractmethod
    def stream(self, **kwargs: Any) -> Generator[BaseCallResponseChunkT, None, None]:
        """A call to an LLM that streams the response in chunks.

        An implementation of this function must yield response chunks that extend
        `BaseCallResponseChunk`. This ensures a consistent API and convenience across
        e.g. different model providers.
        """
        ...  # pragma: no cover

    @abstractmethod
    async def stream_async(
        self, **kwargs: Any
    ) -> AsyncGenerator[BaseCallResponseChunkT, None]:
        """A asynchronous call to an LLM that streams the response in chunks.

        An implementation of this function must yield response chunks that extend
        `BaseCallResponseChunk`. This ensures a consistent API and convenience across
        e.g. different model providers."""
        yield ...  # type: ignore # pragma: no cover
