"""The Call module for generating responses using LLMs."""

from collections.abc import Sequence
from dataclasses import dataclass

from ..content import UserContent
from ..prompts import Prompt
from ..responses import Response
from ..streams import AsyncStream, Stream
from ..types import FormatT, P
from .base_call import BaseCall


@dataclass
class Call(BaseCall[P, Prompt, FormatT]):
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

    def stream_async(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStream[None, FormatT]:
        """Generates an asynchronous streaming response using the LLM."""
        raise NotImplementedError()

    def resume(
        self, response: Response[None, FormatT], content: UserContent | Sequence[UserContent]
    ) -> Response[None, FormatT]:
        """Generate a new response by continuing from a previous response, plus new user content."""
        raise NotImplementedError()

    async def resume_async(
        self, response: Response[None, FormatT], content: UserContent | Sequence[UserContent]
    ) -> Response[None, FormatT]:
        """Generate a new response asynchronously by continuing from a previous response, plus new user content."""
        raise NotImplementedError()

    def resume_stream(
        self, response: Response[None, FormatT], content: UserContent | Sequence[UserContent]
    ) -> Stream[None, FormatT]:
        """Generate a new stream by continuing from a previous response, plus new user content."""
        raise NotImplementedError()

    def resume_stream_async(
        self, response: Response[None, FormatT], content: UserContent | Sequence[UserContent]
    ) -> AsyncStream[None, FormatT]:
        """Generate a new async stream by continuing from a previous response, plus new user content."""
        raise NotImplementedError()
