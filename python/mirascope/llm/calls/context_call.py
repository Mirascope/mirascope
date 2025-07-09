"""The ContextCall module for generating responses using LLMs with context."""

from dataclasses import dataclass

from ..context import Context
from ..prompts import Prompt
from ..responses import Response
from ..streams import AsyncStream, Stream
from ..types import DepsT, P
from .base_context_call import BaseContextCall


@dataclass
class ContextCall(BaseContextCall[P, Prompt, DepsT]):
    """A class for generating responses using LLMs."""

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response:
        """Generates a response using the LLM."""
        raise NotImplementedError()

    async def call_async(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response:
        """Generates an asynchronous response using the LLM."""
        raise NotImplementedError()

    def stream(self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs) -> Stream:
        """Generates a streaming response using the LLM."""
        raise NotImplementedError()

    async def stream_async(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStream:
        """Generates an asynchronous streaming response using the LLM."""
        raise NotImplementedError()
