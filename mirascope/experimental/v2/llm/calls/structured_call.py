"""The StructuredCall module for generating structured responses using LLMs."""

from dataclasses import dataclass
from typing import ParamSpec

from typing_extensions import TypeVar

from ..prompt_templates import PromptTemplate
from ..responses import AsyncStructuredStream, Response, StructuredStream
from ..types import Dataclass
from .base_structured_call import BaseStructuredCall

P = ParamSpec("P")
T = TypeVar("T", bound=Dataclass | None, default=None)


@dataclass
class StructuredCall(BaseStructuredCall[P, PromptTemplate, T]):
    """A class for generating structured responses using LLMs."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Response[T]:
        """Generates a structured response using the LLM."""
        raise NotImplementedError()

    async def call_async(self, *args: P.args, **kwargs: P.kwargs) -> Response[T]:
        """Generates an asynchronous structured response using the LLM."""
        raise NotImplementedError()

    def stream(self, *args: P.args, **kwargs: P.kwargs) -> StructuredStream[T]:
        """Generates a streaming structured response using the LLM."""
        raise NotImplementedError()

    async def stream_async(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStructuredStream[T]:
        """Generates an asynchronous streaming structured response using the LLM."""
        raise NotImplementedError()
