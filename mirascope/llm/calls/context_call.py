"""The ContextCall module for generating responses using LLMs with context."""

from dataclasses import dataclass
from typing import ParamSpec

from typing_extensions import TypeVar

from ..context import Context
from ..prompt_templates import PromptTemplate
from ..responses import AsyncStream, ContextResponse, Stream
from .base_context_call import BaseContextCall

P = ParamSpec("P")
DepsT = TypeVar("DepsT", default=None)


@dataclass
class ContextCall(BaseContextCall[P, PromptTemplate, DepsT]):
    """A class for generating responses using LLMs."""

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> ContextResponse[DepsT]:
        """Generates a response using the LLM."""
        raise NotImplementedError()

    async def call_async(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> ContextResponse[DepsT]:
        """Generates an asynchronous response using the LLM."""
        raise NotImplementedError()

    def stream(self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs) -> Stream:
        """Generates a streaming response using the LLM."""
        raise NotImplementedError()

    async def stream_async(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStream:
        """Generates an asynchronous streaming response using the LLM."""
        raise NotImplementedError()
