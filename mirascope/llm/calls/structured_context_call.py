"""The StructuredContextCall module for generating structured responses using LLMs."""

from dataclasses import dataclass
from typing import ParamSpec

from typing_extensions import TypeVar

from ..context import Context
from ..prompt_templates import PromptTemplate
from ..responses import AsyncStructuredStream, ContextResponse, StructuredStream
from ..types import Dataclass
from .base_structured_context_call import BaseStructuredContextCall

P = ParamSpec("P")
T = TypeVar("T", bound=Dataclass | None, default=None)
DepsT = TypeVar("DepsT", default=None)


@dataclass
class StructuredContextCall(BaseStructuredContextCall[P, PromptTemplate, T, DepsT]):
    """A class for generating structured responses using LLMs."""

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> ContextResponse[DepsT, T]:
        """Generates a structured response using the LLM."""
        raise NotImplementedError()

    async def call_async(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> ContextResponse[DepsT, T]:
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
