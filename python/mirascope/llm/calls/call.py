"""The Call module for generating responses using LLMs."""

from dataclasses import dataclass
from typing import Generic

from ..formatting import FormatT
from ..prompts import AsyncPrompt, Prompt
from ..responses import Response
from ..streams import AsyncStream, Stream
from ..tools import Toolkit, ToolT
from ..types import P
from .base_call import BaseAsyncCall, BaseSyncCall


@dataclass
class Call(
    BaseSyncCall[P, Prompt, Toolkit[ToolT], FormatT, None], Generic[P, ToolT, FormatT]
):
    """A class for generating responses using LLMs."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Response[None, FormatT]:
        """Generates a response using the LLM."""
        raise NotImplementedError()

    def call(self, *args: P.args, **kwargs: P.kwargs) -> Response[None, FormatT]:
        """Generates a response using the LLM."""
        raise NotImplementedError()

    async def call_async(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Response[None, FormatT]:
        """Generates an asynchronous response using the LLM."""
        raise NotImplementedError()

    def stream(self, *args: P.args, **kwargs: P.kwargs) -> Stream[None, FormatT]:
        """Generates a streaming response using the LLM."""
        raise NotImplementedError()

    async def stream_async(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStream[None, FormatT]:
        """Generates an asynchronous streaming response using the LLM."""
        raise NotImplementedError()


@dataclass
class AsyncCall(
    BaseAsyncCall[P, AsyncPrompt, Toolkit[ToolT], FormatT, None],
    Generic[P, ToolT, FormatT],
):
    """A class for generating responses using LLMs asynchronously."""

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
