"""The AsyncCall module for generating responses asynchronously using LLMs."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic

from ..content import UserContent
from ..prompts import AsyncPrompt
from ..response_formatting import FormatT
from ..responses import Response
from ..streams import AsyncStream, BaseStream
from ..tools import Toolkit, ToolT
from ..types import P
from .base_call import BaseCall


@dataclass
class AsyncCall(BaseCall[P, AsyncPrompt, FormatT], Generic[P, ToolT, FormatT]):
    """A class for generating responses using LLMs asynchronously."""

    toolkit: Toolkit[ToolT]
    """The toolkit of tools associated with this call."""

    async def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Response[None, FormatT]:
        """Generates a response using the LLM asynchronously."""
        raise NotImplementedError()

    async def call(self, *args: P.args, **kwargs: P.kwargs) -> Response[None, FormatT]:
        """Generates a response using the LLM asynchronously."""
        raise NotImplementedError()

    async def call_async(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Response[None, FormatT]:
        """Generates an asynchronous response using the LLM."""
        raise NotImplementedError()

    async def stream(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStream[None, FormatT]:
        """Generates a streaming response using the LLM asynchronously."""
        raise NotImplementedError()

    async def stream_async(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStream[None, FormatT]:
        """Generates an asynchronous streaming response using the LLM."""
        raise NotImplementedError()

    async def resume(
        self,
        output: Response[None, FormatT] | BaseStream[None, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> Response[None, FormatT]:
        """Generate a new response by continuing from a previous output, plus new user content."""
        raise NotImplementedError()

    async def resume_async(
        self,
        output: Response[None, FormatT] | BaseStream[None, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> Response[None, FormatT]:
        """Generate a new response asynchronously by continuing from a previous output, plus new user content."""
        raise NotImplementedError()

    async def resume_stream(
        self,
        output: Response[None, FormatT] | BaseStream[None, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> AsyncStream[None, FormatT]:
        """Generate a new stream by continuing from a previous output, plus new user content."""
        raise NotImplementedError()

    async def resume_stream_async(
        self,
        output: Response[None, FormatT] | BaseStream[None, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> AsyncStream[None, FormatT]:
        """Generate a new async stream by continuing from a previous output, plus new user content."""
        raise NotImplementedError()
