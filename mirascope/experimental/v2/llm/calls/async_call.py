"""The AsyncCall module for generating responses asynchronously using LLMs."""

from dataclasses import dataclass
from typing import ParamSpec

from ..prompt_templates import AsyncPromptTemplate
from ..responses import AsyncStream, Response
from .base_call import BaseCall

P = ParamSpec("P")


@dataclass
class AsyncCall(BaseCall[P, AsyncPromptTemplate]):
    """A class for generating responses using LLMs asynchronously."""

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Response:
        """Generates a response using the LLM asynchronously."""
        raise NotImplementedError()

    async def call_async(self, *args: P.args, **kwargs: P.kwargs) -> Response:
        """Generates an asynchronous response using the LLM."""
        return await self(*args, **kwargs)

    async def stream(self, *args: P.args, **kwargs: P.kwargs) -> AsyncStream:
        """Generates a streaming response using the LLM asynchronously."""
        raise NotImplementedError()

    async def stream_async(self, *args: P.args, **kwargs: P.kwargs) -> AsyncStream:
        """Generates an asynchronous streaming response using the LLM."""
        return await self.stream(*args, **kwargs)
