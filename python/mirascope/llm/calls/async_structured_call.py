"""The AsyncStructuredCall module for generating structured responses using LLMs."""

from collections.abc import Sequence
from dataclasses import dataclass

from ..content import UserContent
from ..prompts import AsyncPrompt
from ..responses import Response
from ..streams import AsyncStructuredStream
from ..types import P, T
from .base_structured_call import BaseStructuredCall


@dataclass
class AsyncStructuredCall(BaseStructuredCall[P, AsyncPrompt, T]):
    """A class for generating structured responses using LLMs asynchronously."""

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Response[None, T]:
        """Generates a structured response using the LLM asynchronously."""
        raise NotImplementedError()

    async def call(self, *args: P.args, **kwargs: P.kwargs) -> Response[None, T]:
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

    async def resume(
        self, response: Response[None, T], content: UserContent | Sequence[UserContent]
    ) -> Response[None, T]:
        """Generate a new response by continuing from a previous response, plus new user content."""
        raise NotImplementedError()

    async def resume_async(
        self, response: Response[None, T], content: UserContent | Sequence[UserContent]
    ) -> Response[None, T]:
        """Generate a new response asynchronously by continuing from a previous response, plus new user content."""
        raise NotImplementedError()

    async def resume_stream(
        self, response: Response[None, T], content: UserContent | Sequence[UserContent]
    ) -> AsyncStructuredStream[None, T]:
        """Generate a new stream by continuing from a previous response, plus new user content."""
        raise NotImplementedError()

    async def resume_stream_async(
        self, response: Response[None, T], content: UserContent | Sequence[UserContent]
    ) -> AsyncStructuredStream[None, T]:
        """Generate a new async stream by continuing from a previous response, plus new user content."""
        raise NotImplementedError()
