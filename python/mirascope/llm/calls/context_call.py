"""The ContextCall module for generating responses using LLMs with context."""

from dataclasses import dataclass
from typing import Generic

from ..context import Context, DepsT
from ..formatting import FormatT
from ..messages import UserContent
from ..prompts import Prompt
from ..responses import AsyncStreamResponse, Response, StreamResponse
from ..tools import AsyncContextToolkit, ContextToolkit
from ..types import P
from .base_call import BaseCall


@dataclass
class ContextCall(
    BaseCall[P, Prompt, ContextToolkit[DepsT], FormatT],
    Generic[P, DepsT, FormatT],
):
    """A class for generating responses using LLMs."""

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response[FormatT]:
        """Generates a response using the LLM."""
        raise NotImplementedError()

    def call(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response[FormatT]:
        """Generates a response using the LLM."""
        raise NotImplementedError()

    def stream(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> StreamResponse[FormatT]:
        """Generates a streaming response using the LLM."""
        raise NotImplementedError()

    def resume(
        self,
        ctx: Context[DepsT],
        response: Response[FormatT]
        | StreamResponse[FormatT]
        | AsyncStreamResponse[FormatT],
        content: UserContent,
    ) -> Response[FormatT]:
        """Generate a new response by continuing from a previous output, plus new user content."""
        raise NotImplementedError()

    def resume_stream(
        self,
        ctx: Context[DepsT],
        response: Response[FormatT]
        | StreamResponse[FormatT]
        | AsyncStreamResponse[FormatT],
        content: UserContent,
    ) -> StreamResponse[FormatT]:
        """Generate a new stream by continuing from a previous output, plus new user content."""
        raise NotImplementedError()


@dataclass
class AsyncContextCall(
    BaseCall[P, Prompt, AsyncContextToolkit[DepsT], FormatT],
    Generic[P, DepsT, FormatT],
):
    """A class for generating responses using LLMs asynchronously."""

    async def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response[FormatT]:
        """Generates a response using the LLM asynchronously."""
        raise NotImplementedError()

    async def call(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response[FormatT]:
        """Generates a response using the LLM asynchronously."""
        raise NotImplementedError()

    async def stream(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStreamResponse[FormatT]:
        """Generates a streaming response using the LLM asynchronously."""
        raise NotImplementedError()

    async def resume(
        self,
        ctx: Context[DepsT],
        response: Response[FormatT]
        | StreamResponse[FormatT]
        | AsyncStreamResponse[FormatT],
        content: UserContent,
    ) -> Response[FormatT]:
        """Generate a new response by continuing from a previous output, plus new user content."""
        raise NotImplementedError()

    async def resume_stream(
        self,
        ctx: Context[DepsT],
        response: Response[FormatT]
        | StreamResponse[FormatT]
        | AsyncStreamResponse[FormatT],
        content: UserContent,
    ) -> AsyncStreamResponse[FormatT]:
        """Generate a new stream by continuing from a previous output, plus new user content."""
        raise NotImplementedError()
