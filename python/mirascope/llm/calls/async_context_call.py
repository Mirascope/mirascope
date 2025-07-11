"""The AsyncContextCall module for generating responses asynchronously using LLMs."""

from collections.abc import Sequence
from dataclasses import dataclass

from ..content import UserContent
from ..context import Context
from ..prompts import AsyncPrompt
from ..responses import Response
from ..streams import AsyncStream
from ..types import DepsT, P
from .base_context_call import BaseContextCall


@dataclass
class AsyncContextCall(BaseContextCall[P, AsyncPrompt, DepsT]):
    """A class for generating responses using LLMs asynchronously."""

    async def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response[DepsT, None]:
        """Generates a response using the LLM asynchronously."""
        raise NotImplementedError()

    async def call(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response[DepsT, None]:
        """Generates a response using the LLM asynchronously."""
        raise NotImplementedError()

    async def call_async(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response[DepsT, None]:
        """Generates an asynchronous response using the LLM."""
        return await self(ctx, *args, **kwargs)

    async def stream(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStream[DepsT]:
        """Generates a streaming response using the LLM asynchronously."""
        raise NotImplementedError()

    async def stream_async(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStream[DepsT]:
        """Generates an asynchronous streaming response using the LLM."""
        return await self.stream(ctx, *args, **kwargs)

    async def resume(
        self,
        response: Response[DepsT, None],
        content: UserContent | Sequence[UserContent],
    ) -> Response[DepsT, None]:
        """Generate a new response by continuing from a previous response, plus new user content."""
        raise NotImplementedError()

    async def resume_async(
        self,
        response: Response[DepsT, None],
        content: UserContent | Sequence[UserContent],
    ) -> Response[DepsT, None]:
        """Generate a new response asynchronously by continuing from a previous response, plus new user content."""
        raise NotImplementedError()

    async def resume_stream(
        self,
        response: Response[DepsT, None],
        content: UserContent | Sequence[UserContent],
    ) -> AsyncStream[DepsT]:
        """Generate a new stream by continuing from a previous response, plus new user content."""
        raise NotImplementedError()

    async def resume_stream_async(
        self,
        response: Response[DepsT, None],
        content: UserContent | Sequence[UserContent],
    ) -> AsyncStream[DepsT]:
        """Generate a new async stream by continuing from a previous response, plus new user content."""
        raise NotImplementedError()
