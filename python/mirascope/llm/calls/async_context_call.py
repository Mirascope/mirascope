"""The AsyncContextCall module for generating responses asynchronously using LLMs."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic

from ..content import UserContent
from ..context import Context, DepsT
from ..prompts import AsyncPrompt
from ..response_formatting import FormatT
from ..responses import Response
from ..streams import AsyncStream, BaseStream
from ..tools import ContextToolkit, ContextToolT
from ..types import P
from .base_call import BaseCall


@dataclass
class AsyncContextCall(
    BaseCall[P, AsyncPrompt, FormatT], Generic[P, ContextToolT, DepsT, FormatT]
):
    """A class for generating responses using LLMs asynchronously."""

    toolkit: ContextToolkit[ContextToolT, DepsT]
    """The toolkit of tools associated with this call."""

    async def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response[DepsT, FormatT]:
        """Generates a response using the LLM asynchronously."""
        raise NotImplementedError()

    async def call(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response[DepsT, FormatT]:
        """Generates a response using the LLM asynchronously."""
        raise NotImplementedError()

    async def call_async(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response[DepsT, FormatT]:
        """Generates an asynchronous response using the LLM."""
        raise NotImplementedError()

    async def stream(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStream[DepsT, FormatT]:
        """Generates a streaming response using the LLM asynchronously."""
        raise NotImplementedError()

    async def stream_async(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStream[DepsT, FormatT]:
        """Generates an asynchronous streaming response using the LLM."""
        raise NotImplementedError()

    async def resume(
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

    async def resume_stream(
        self,
        output: Response[DepsT, FormatT] | BaseStream[DepsT, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> AsyncStream[DepsT, FormatT]:
        """Generate a new stream by continuing from a previous output, plus new user content."""
        raise NotImplementedError()

    async def resume_stream_async(
        self,
        output: Response[DepsT, FormatT] | BaseStream[DepsT, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> AsyncStream[DepsT, FormatT]:
        """Generate a new async stream by continuing from a previous output, plus new user content."""
        raise NotImplementedError()
