"""A base abstract interface for calling LLMs."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncGenerator, ClassVar, Generator, Optional

from pydantic import BaseModel, ConfigDict

from .prompts import BasePrompt
from .types import BaseCallResponse, BaseCallResponseChunk


class BaseCall(BasePrompt, ABC):
    """The base class abstract interface for calling LLMs."""

    api_key: Optional[str] = None
    base_url: Optional[str] = None

    class CallParams(BaseModel):
        """The parameters with which to make a call."""

        model: str

        model_config = ConfigDict(extra="allow")

    call_params: ClassVar[CallParams]

    @abstractmethod
    def call(self, params: CallParams) -> BaseCallResponse:
        """A call to an LLM.

        An implementation of this function must return a response that extends
        `BaseCallResponse`. This ensures a consistent API and convenience across e.g.
        different model providers.
        """
        ...  # pragma: no cover

    @abstractmethod
    async def call_async(self, params: CallParams) -> BaseCallResponse:
        """An asynchronous call to an LLM.

        An implementation of this function must return a response that extends
        `BaseCallResponse`. This ensures a consistent API and convenience across e.g.
        different model providers.
        """
        ...  # pragma: no cover

    @abstractmethod
    def stream(
        self, params: CallParams
    ) -> Generator[BaseCallResponseChunk, None, None]:
        """A call to an LLM that streams the response in chunks.

        An implementation of this function must yield response chunks that extend
        `BaseCallResponseChunk`. This ensures a consistent API and convenience across
        e.g. different model providers.
        """
        ...  # pragma: no cover

    @abstractmethod
    async def stream_async(
        self, params: CallParams
    ) -> AsyncGenerator[BaseCallResponseChunk, None]:
        """A asynchronous call to an LLM that streams the response in chunks.

        An implementation of this function must yield response chunks that extend
        `BaseCallResponseChunk`. This ensures a consistent API and convenience across
        e.g. different model providers."""
        ...  # pragma: no cover
