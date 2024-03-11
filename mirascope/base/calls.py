"""A base abstract interface for calling LLMs."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncGenerator, ClassVar, Generator, Optional

from .prompts import BasePrompt
from .types import BaseCallParams, BaseCallResponse, BaseCallResponseChunk


class BaseCall(BasePrompt, ABC):
    """The base class abstract interface for calling LLMs."""

    api_key: Optional[str] = None
    base_url: Optional[str] = None

    call_params: ClassVar[BaseCallParams]

    @abstractmethod
    def call(self, params: Optional[BaseCallParams] = None) -> BaseCallResponse:
        """A call to an LLM.

        An implementation of this function must return a response that extends
        `BaseCallResponse`. This ensures a consistent API and convenience across e.g.
        different model providers.
        """
        ...  # pragma: no cover

    @abstractmethod
    async def call_async(
        self, params: Optional[BaseCallParams] = None
    ) -> BaseCallResponse:
        """An asynchronous call to an LLM.

        An implementation of this function must return a response that extends
        `BaseCallResponse`. This ensures a consistent API and convenience across e.g.
        different model providers.
        """
        ...  # pragma: no cover

    @abstractmethod
    def stream(
        self, params: Optional[BaseCallParams] = None
    ) -> Generator[BaseCallResponseChunk, None, None]:
        """A call to an LLM that streams the response in chunks.

        An implementation of this function must yield response chunks that extend
        `BaseCallResponseChunk`. This ensures a consistent API and convenience across
        e.g. different model providers.
        """
        ...  # pragma: no cover

    @abstractmethod
    async def stream_async(
        self, params: Optional[BaseCallParams] = None
    ) -> AsyncGenerator[BaseCallResponseChunk, None]:
        """A asynchronous call to an LLM that streams the response in chunks.

        An implementation of this function must yield response chunks that extend
        `BaseCallResponseChunk`. This ensures a consistent API and convenience across
        e.g. different model providers."""
        ...  # pragma: no cover
