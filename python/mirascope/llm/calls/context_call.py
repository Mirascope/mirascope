"""The ContextCall module for generating responses using LLMs with context."""

from collections.abc import Sequence
from dataclasses import dataclass

from ..content import UserContent
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
    ) -> Response[DepsT, None]:
        """Generates a response using the LLM."""
        raise NotImplementedError()

    def call(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response[DepsT, None]:
        """Generates a response using the LLM."""
        raise NotImplementedError()

    async def call_async(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response[DepsT, None]:
        """Generates an asynchronous response using the LLM."""
        raise NotImplementedError()

    def stream(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Stream[DepsT]:
        """Generates a streaming response using the LLM."""
        raise NotImplementedError()

    async def stream_async(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStream[DepsT]:
        """Generates an asynchronous streaming response using the LLM."""
        raise NotImplementedError()

    def resume(
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

    def resume_stream(
        self,
        response: Response[DepsT, None],
        content: UserContent | Sequence[UserContent],
    ) -> Stream[DepsT]:
        """Generate a new stream by continuing from a previous response, plus new user content."""
        raise NotImplementedError()

    def resume_stream_async(
        self,
        response: Response[DepsT, None],
        content: UserContent | Sequence[UserContent],
    ) -> AsyncStream[DepsT]:
        """Generate a new async stream by continuing from a previous response, plus new user content."""
        raise NotImplementedError()
