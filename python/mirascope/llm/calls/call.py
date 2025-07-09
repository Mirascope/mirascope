"""The Call module for generating responses using LLMs."""

from dataclasses import dataclass

from ..prompts import Prompt
from ..responses import Response
from ..streams import AsyncStream, Stream
from ..types import P
from .base_call import BaseCall


@dataclass
class Call(BaseCall[P, Prompt]):
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

    def stream_async(self, *args: P.args, **kwargs: P.kwargs) -> AsyncStream:
        """Generates an asynchronous streaming response using the LLM."""
        raise NotImplementedError()
