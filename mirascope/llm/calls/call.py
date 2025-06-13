"""The Call module for generating responses using LLMs."""

from dataclasses import dataclass
from typing import ParamSpec

from ..prompt_templates import PromptTemplate
from ..responses import AsyncStream, Response, Stream
from .base_call import BaseCall

P = ParamSpec("P")


@dataclass
class Call(BaseCall[P, PromptTemplate]):
    """A class for generating responses using LLMs."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Response:
        """Generates a response using the LLM."""
        raise NotImplementedError()

    async def call_async(self, *args: P.args, **kwargs: P.kwargs) -> Response:
        """Generates an asynchronous response using the LLM."""
        raise NotImplementedError()

    def stream(self, *args: P.args, **kwargs: P.kwargs) -> Stream:
        """Generates a streaming response using the LLM."""
        raise NotImplementedError()

    async def stream_async(self, *args: P.args, **kwargs: P.kwargs) -> AsyncStream:
        """Generates an asynchronous streaming response using the LLM."""
        raise NotImplementedError()
