"""The AsyncStructuredContextCall module for generating structured responses using LLMs."""

from collections.abc import Sequence
from dataclasses import dataclass

from ..content import UserContent
from ..context import Context
from ..prompts import AsyncPrompt
from ..responses import Response
from ..streams import AsyncStream
from ..types import DepsT, FormatT, P
from .base_structured_context_call import BaseStructuredContextCall


@dataclass
class AsyncStructuredContextCall(
    BaseStructuredContextCall[P, AsyncPrompt, FormatT, DepsT]
):
    """A class for generating structured responses using LLMs asynchronously."""

    async def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response[DepsT, FormatT]:
        """Generates a structured response using the LLM asynchronously."""
        raise NotImplementedError()

    async def call(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response[DepsT, FormatT]:
        """Generates a structured response using the LLM asynchronously."""
        raise NotImplementedError()

    async def call_async(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response[DepsT, FormatT]:
        """Generates an asynchronous structured response using the LLM."""
        return await self(ctx, *args, **kwargs)

    async def stream(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStream[DepsT, FormatT]:
        """Generates a streaming structured response using the LLM asynchronously."""
        raise NotImplementedError()

    async def stream_async(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStream[DepsT, FormatT]:
        """Generates an asynchronous streaming structured response using the LLM."""
        return await self.stream(ctx, *args, **kwargs)

    async def resume(
        self,
        response: Response[DepsT, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> Response[DepsT, FormatT]:
        """Generate a new response by continuing from a previous response, plus new user content."""
        raise NotImplementedError()

    async def resume_async(
        self,
        response: Response[DepsT, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> Response[DepsT, FormatT]:
        """Generate a new response asynchronously by continuing from a previous response, plus new user content."""
        raise NotImplementedError()

    async def resume_stream(
        self,
        response: Response[DepsT, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> AsyncStream[DepsT, FormatT]:
        """Generate a new stream by continuing from a previous response, plus new user content."""
        raise NotImplementedError()

    async def resume_stream_async(
        self,
        response: Response[DepsT, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> AsyncStream[DepsT, FormatT]:
        """Generate a new async stream by continuing from a previous response, plus new user content."""
        raise NotImplementedError()
