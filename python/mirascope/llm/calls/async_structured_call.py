"""The AsyncStructuredCall module for generating structured responses using LLMs."""

from collections.abc import Sequence
from dataclasses import dataclass

from ..content import UserContent
from ..prompts import AsyncPrompt
from ..responses import Response
from ..streams import AsyncStream
from ..types import FormatT, P
from .base_structured_call import BaseStructuredCall


@dataclass
class AsyncStructuredCall(BaseStructuredCall[P, AsyncPrompt, FormatT]):
    """A class for generating structured responses using LLMs asynchronously."""

    async def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Response[None, FormatT]:
        """Generates a structured response using the LLM asynchronously."""
        raise NotImplementedError()

    async def call(self, *args: P.args, **kwargs: P.kwargs) -> Response[None, FormatT]:
        """Generates a structured response using the LLM asynchronously."""
        raise NotImplementedError()

    async def call_async(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Response[None, FormatT]:
        """Generates an asynchronous structured response using the LLM."""
        return await self(*args, **kwargs)

    async def stream(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStream[None, FormatT]:
        """Generates a streaming structured response using the LLM asynchronously."""
        raise NotImplementedError()

    async def stream_async(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStream[None, FormatT]:
        """Generates an asynchronous streaming structured response using the LLM."""
        return await self.stream(*args, **kwargs)

    async def resume(
        self,
        response: Response[None, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> Response[None, FormatT]:
        """Generate a new response by continuing from a previous response, plus new user content."""
        raise NotImplementedError()

    async def resume_async(
        self,
        response: Response[None, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> Response[None, FormatT]:
        """Generate a new response asynchronously by continuing from a previous response, plus new user content."""
        raise NotImplementedError()

    async def resume_stream(
        self,
        response: Response[None, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> AsyncStream[None, FormatT]:
        """Generate a new stream by continuing from a previous response, plus new user content."""
        raise NotImplementedError()

    async def resume_stream_async(
        self,
        response: Response[None, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> AsyncStream[None, FormatT]:
        """Generate a new async stream by continuing from a previous response, plus new user content."""
        raise NotImplementedError()
