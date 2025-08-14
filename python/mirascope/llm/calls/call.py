"""The Call module for generating responses using LLMs."""

from dataclasses import dataclass
from typing import Generic

from ..formatting import FormatT
from ..messages import UserContent
from ..prompts import AsyncPrompt, Prompt
from ..responses import AsyncStreamResponse, Response, StreamResponse
from ..tools import ToolT
from ..types import P
from .base_call import BaseCall

# TODO(@dandelion): Revisit resume API to have clear arg types for content
# (vs UserMessagePromotable which may be opaque), and rename `output` arg


@dataclass
class Call(BaseCall[P, Prompt, ToolT, FormatT], Generic[P, ToolT, FormatT]):
    """A class for generating responses using LLMs."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Response[FormatT]:
        """Generates a response using the LLM."""
        raise NotImplementedError()

    def call(self, *args: P.args, **kwargs: P.kwargs) -> Response[FormatT]:
        """Generates a response using the LLM."""
        raise NotImplementedError()

    def stream(self, *args: P.args, **kwargs: P.kwargs) -> StreamResponse[FormatT]:
        """Generates a streaming response using the LLM."""
        raise NotImplementedError()

    def resume(
        self,
        response: Response[FormatT]
        | StreamResponse[FormatT]
        | AsyncStreamResponse[FormatT],
        content: UserContent,
    ) -> Response[FormatT]:
        """Generate a new response by continuing from a previous output, plus new user content."""
        raise NotImplementedError()

    def resume_stream(
        self,
        response: Response[FormatT]
        | StreamResponse[FormatT]
        | AsyncStreamResponse[FormatT],
        content: UserContent,
    ) -> StreamResponse[FormatT]:
        """Generate a new stream by continuing from a previous output, plus new user content."""
        raise NotImplementedError()


@dataclass
class AsyncCall(
    BaseCall[P, AsyncPrompt, ToolT, FormatT],
    Generic[P, ToolT, FormatT],
):
    """A class for generating responses using LLMs asynchronously."""

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Response[FormatT]:
        """Generates a response using the LLM asynchronously."""
        raise NotImplementedError()

    async def call(self, *args: P.args, **kwargs: P.kwargs) -> Response[FormatT]:
        """Generates a response using the LLM asynchronously."""
        raise NotImplementedError()

    async def stream(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStreamResponse[FormatT]:
        """Generates a streaming response using the LLM asynchronously."""
        raise NotImplementedError()

    async def resume(
        self,
        response: Response[FormatT]
        | StreamResponse[FormatT]
        | AsyncStreamResponse[FormatT],
        content: UserContent,
    ) -> Response[FormatT]:
        """Generate a new response by continuing from a previous output, plus new user content."""
        raise NotImplementedError()

    async def resume_stream(
        self,
        response: Response[FormatT]
        | StreamResponse[FormatT]
        | AsyncStreamResponse[FormatT],
        content: UserContent,
    ) -> AsyncStreamResponse[FormatT]:
        """Generate a new stream by continuing from a previous output, plus new user content."""
        raise NotImplementedError()
