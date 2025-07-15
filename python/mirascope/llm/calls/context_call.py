"""The ContextCall module for generating responses using LLMs with context."""

from collections.abc import Sequence
from dataclasses import dataclass

from ..content import UserContent
from ..context import Context, DepsT
from ..prompts import Prompt
from ..response_formatting import FormatT
from ..responses import Response
from ..streams import AsyncStream, BaseStream, Stream
from ..tools import ContextToolT
from ..types import P
from .base_context_call import BaseContextCall


@dataclass
class ContextCall(BaseContextCall[P, Prompt, ContextToolT, DepsT, FormatT]):
    """A class for generating responses using LLMs."""

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response[DepsT, FormatT]:
        """Generates a response using the LLM."""
        raise NotImplementedError()

    def call(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response[DepsT, FormatT]:
        """Generates a response using the LLM."""
        raise NotImplementedError()

    async def call_async(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response[DepsT, FormatT]:
        """Generates an asynchronous response using the LLM."""
        raise NotImplementedError()

    def stream(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Stream[DepsT, FormatT]:
        """Generates a streaming response using the LLM."""
        raise NotImplementedError()

    async def stream_async(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStream[DepsT, FormatT]:
        """Generates an asynchronous streaming response using the LLM."""
        raise NotImplementedError()

    def resume(
        self,
        output: Response[DepsT, FormatT] | BaseStream[DepsT, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> Response[DepsT, FormatT]:
        """Generate a new response by continuing from a previous output, plus new user content."""
        raise NotImplementedError()

    async def resume_async(
        self,
        output: Response[DepsT, FormatT] | BaseStream[DepsT, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> Response[DepsT, FormatT]:
        """Generate a new response asynchronously by continuing from a previous output, plus new user content."""
        raise NotImplementedError()

    def resume_stream(
        self,
        output: Response[DepsT, FormatT] | BaseStream[DepsT, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> Stream[DepsT, FormatT]:
        """Generate a new stream by continuing from a previous output, plus new user content."""
        raise NotImplementedError()

    async def resume_stream_async(
        self,
        output: Response[DepsT, FormatT] | BaseStream[DepsT, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> AsyncStream[DepsT, FormatT]:
        """Generate a new async stream by continuing from a previous output, plus new user content."""
        raise NotImplementedError()
