"""The AsyncContextCall module for generating responses asynchronously using LLMs."""

from dataclasses import dataclass
from typing import ParamSpec

from typing_extensions import TypeVar

from ..context import Context
from ..prompts import AsyncPrompt
from ..responses import AsyncStream, Response
from .base_context_call import BaseContextCall

P = ParamSpec("P")
DepsT = TypeVar("DepsT", default=None)


@dataclass
class AsyncContextCall(BaseContextCall[P, AsyncPrompt, DepsT]):
    """A class for generating responses using LLMs asynchronously."""

    async def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response:
        """Generates a response using the LLM asynchronously."""
        raise NotImplementedError()

    async def call_async(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response:
        """Generates an asynchronous response using the LLM."""
        return await self(ctx, *args, **kwargs)

    async def stream(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStream:
        """Generates a streaming response using the LLM asynchronously."""
        raise NotImplementedError()

    async def stream_async(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStream:
        """Generates an asynchronous streaming response using the LLM."""
        return await self.stream(ctx, *args, **kwargs)
