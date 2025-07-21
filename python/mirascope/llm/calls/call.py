"""The Call module for generating responses using LLMs."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic

from ..content import UserContent
from ..formatting import FormatT
from ..prompts import AsyncPrompt, Prompt
from ..responses import Response
from ..streams import AsyncStream, BaseStream, Stream
from ..tools import ToolT
from ..types import P
from .base_call import BaseCall


@dataclass
class Call(BaseCall[P, Prompt, ToolT, FormatT], Generic[P, ToolT, FormatT]):
    """A class for generating responses using LLMs."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Response[FormatT]:
        """Generates a response using the LLM."""
        raise NotImplementedError()

    def call(self, *args: P.args, **kwargs: P.kwargs) -> Response[FormatT]:
        """Generates a response using the LLM."""
        raise NotImplementedError()

    def stream(self, *args: P.args, **kwargs: P.kwargs) -> Stream[FormatT]:
        """Generates a streaming response using the LLM."""
        raise NotImplementedError()

    def resume(
        self,
        output: Response[FormatT] | BaseStream[FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> Response[FormatT]:
        """Generate a new response by continuing from a previous output, plus new user content."""
        raise NotImplementedError()

    def resume_stream(
        self,
        output: Response[FormatT] | BaseStream[FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> Stream[FormatT]:
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

    async def stream(self, *args: P.args, **kwargs: P.kwargs) -> AsyncStream[FormatT]:
        """Generates a streaming response using the LLM asynchronously."""
        raise NotImplementedError()

    async def resume(
        self,
        output: Response[FormatT] | BaseStream[FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> Response[FormatT]:
        """Generate a new response by continuing from a previous output, plus new user content."""
        raise NotImplementedError()

    async def resume_stream(
        self,
        output: Response[FormatT] | BaseStream[FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> AsyncStream[FormatT]:
        """Generate a new stream by continuing from a previous output, plus new user content."""
        raise NotImplementedError()
