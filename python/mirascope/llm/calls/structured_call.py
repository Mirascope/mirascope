"""The StructuredCall module for generating structured responses using LLMs."""

from dataclasses import dataclass

from ..prompts import Prompt
from ..responses import Response
from ..streams import AsyncStructuredStream, StructuredStream
from ..types import FormatT, P
from .base_structured_call import BaseStructuredCall


@dataclass
class StructuredCall(BaseStructuredCall[P, Prompt, FormatT]):
    """A class for generating structured responses using LLMs."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Response[FormatT]:
        """Generates a structured response using the LLM."""
        raise NotImplementedError()

    async def call_async(self, *args: P.args, **kwargs: P.kwargs) -> Response[FormatT]:
        """Generates an asynchronous structured response using the LLM."""
        raise NotImplementedError()

    def stream(self, *args: P.args, **kwargs: P.kwargs) -> StructuredStream[FormatT]:
        """Generates a streaming structured response using the LLM."""
        raise NotImplementedError()

    async def stream_async(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStructuredStream[FormatT]:
        """Generates an asynchronous streaming structured response using the LLM."""
        raise NotImplementedError()
