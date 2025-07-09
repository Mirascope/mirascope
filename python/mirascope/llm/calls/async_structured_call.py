"""The AsyncStructuredCall module for generating structured responses using LLMs."""

from dataclasses import dataclass
from typing import ParamSpec

from typing_extensions import TypeVar

from ..prompts import AsyncPrompt
from ..responses import Response
from ..streams import AsyncStructuredStream
from .base_structured_call import BaseStructuredCall

P = ParamSpec("P")
T = TypeVar("T", bound=object | None, default=None)


@dataclass
class AsyncStructuredCall(BaseStructuredCall[P, AsyncPrompt, T]):
    """A class for generating structured responses using LLMs asynchronously."""

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Response[None, T]:
        """Generates a structured response using the LLM asynchronously."""
        raise NotImplementedError()

    async def call_async(self, *args: P.args, **kwargs: P.kwargs) -> Response[None, T]:
        """Generates an asynchronous structured response using the LLM."""
        return await self(*args, **kwargs)

    async def stream(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStructuredStream[None, T]:
        """Generates a streaming structured response using the LLM asynchronously."""
        raise NotImplementedError()

    async def stream_async(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStructuredStream[None, T]:
        """Generates an asynchronous streaming structured response using the LLM."""
        return await self.stream(*args, **kwargs)
