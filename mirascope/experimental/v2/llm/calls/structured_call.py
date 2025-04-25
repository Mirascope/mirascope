"""The StructuredCall module for generating structured responses using LLMs."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Generic, ParamSpec

from typing_extensions import TypeVar

from ..messages import AsyncPromptTemplate
from ..models import LLM
from ..response_formatting import ResponseFormat
from ..responses import AsyncStructuredStream, Response, StructuredStream
from ..tools import ToolDef

P = ParamSpec("P")
T = TypeVar("T", default=None)


@dataclass
class BaseStructuredCall(Generic[P, T]):
    """A base class for generating responses using LLMs."""

    model: LLM
    """The LLM model used for generating responses."""

    tools: Sequence[ToolDef] | None
    """The tools to be used with the LLM."""

    response_format: ResponseFormat[T]
    """The response format for the generated response."""

    fn: Callable[P, AsyncPromptTemplate[P]]
    """The function that generates the prompt template."""


@dataclass
class StructuredCall(BaseStructuredCall[P, T]):
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


@dataclass
class AsyncStructuredCall(BaseStructuredCall[P, T]):
    """A class for generating structured responses using LLMs asynchronously."""

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Response[T]:
        """Generates a structured response using the LLM asynchronously."""
        raise NotImplementedError()

    async def call_async(self, *args: P.args, **kwargs: P.kwargs) -> Response[T]:
        """Generates an asynchronous structured response using the LLM."""
        return await self(*args, **kwargs)

    async def stream(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStructuredStream[T]:
        """Generates a streaming structured response using the LLM asynchronously."""
        raise NotImplementedError()

    async def stream_async(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStructuredStream[T]:
        """Generates an asynchronous streaming structured response using the LLM."""
        return await self.stream(*args, **kwargs)
