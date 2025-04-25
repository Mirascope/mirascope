"""The StructuredContextCall module for generating structured responses using LLMs."""

from dataclasses import dataclass
from typing import Generic, ParamSpec

from typing_extensions import TypeVar

from ..contexts import Context
from ..messages import PromptTemplate
from ..responses import AsyncStructuredStream, ContextResponse, StructuredStream
from .base_structured_call import BaseStructuredCall

P = ParamSpec("P")
T = TypeVar("T", default=None)
DepsT = TypeVar("DepsT", default=None)


@dataclass
class StructuredContextCall(
    BaseStructuredCall[P, PromptTemplate, T], Generic[P, T, DepsT]
):
    """A class for generating structured responses using LLMs."""

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> ContextResponse[T, DepsT]:
        """Generates a structured response using the LLM."""
        raise NotImplementedError()

    async def call_async(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> ContextResponse[T, DepsT]:
        """Generates an asynchronous structured response using the LLM."""
        raise NotImplementedError()

    def stream(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> StructuredStream[T]:
        """Generates a streaming structured response using the LLM."""
        raise NotImplementedError()

    async def stream_async(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStructuredStream[T]:
        """Generates an asynchronous streaming structured response using the LLM."""
        raise NotImplementedError()
