"""The StructuredContextCall module for generating structured responses using LLMs."""

from dataclasses import dataclass

from ..context import Context
from ..prompts import Prompt
from ..responses import Response
from ..streams import AsyncStructuredStream, StructuredStream
from ..types import DepsT, FormatT, P
from .base_structured_context_call import BaseStructuredContextCall


@dataclass
class StructuredContextCall(BaseStructuredContextCall[P, Prompt, FormatT, DepsT]):
    """A class for generating structured responses using LLMs."""

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response[DepsT, FormatT]:
        """Generates a structured response using the LLM."""
        raise NotImplementedError()

    async def call_async(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response[DepsT, FormatT]:
        """Generates an asynchronous structured response using the LLM."""
        raise NotImplementedError()

    def stream(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> StructuredStream[DepsT, FormatT]:
        """Generates a streaming structured response using the LLM."""
        raise NotImplementedError()

    async def stream_async(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStructuredStream[DepsT, FormatT]:
        """Generates an asynchronous streaming structured response using the LLM."""
        raise NotImplementedError()
