"""The Generations module for generating responses using LLMs."""

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Generic, ParamSpec, Protocol, TypeVar, overload

from typing_extensions import Unpack

from .messages import AsyncPromptTemplate, PromptTemplate
from .models import Client, Params
from .response_formatting import ResponseFormat
from .responses import Response
from .streams import AsyncStream, AsyncStructuredStream, Stream, StructuredStream
from .tools import ToolDef

if TYPE_CHECKING:
    from .models.anthropic import (
        ANTHROPIC_REGISTERED_LLMS,
        AnthropicClient,
        AnthropicParams,
    )
    from .models.context import REGISTERED_LLMS
    from .models.google import (
        GOOGLE_REGISTERED_LLMS,
        GoogleClient,
        GoogleParams,
    )
    from .models.openai import (
        OPENAI_REGISTERED_LLMS,
        OpenAIClient,
        OpenAIParams,
    )

P = ParamSpec("P")
T = TypeVar("T")


class Generation(Generic[P]):
    """A class for generating responses using LLMs."""

    def __init__(self, fn: Callable[P, PromptTemplate[P]]) -> None:
        """Initializes a `Generation` instance."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Response:
        """Generates a response using the LLM."""
        raise NotImplementedError()

    def stream(self, *args: P.args, **kwargs: P.kwargs) -> Stream:
        """Generates a streaming response using the LLM."""
        raise NotImplementedError()

    async def call_async(self, *args: P.args, **kwargs: P.kwargs) -> Response:
        """Generates an asynchronous response using the LLM."""
        raise NotImplementedError()

    async def stream_async(self, *args: P.args, **kwargs: P.kwargs) -> AsyncStream:
        """Generates an asynchronous streaming response using the LLM."""
        raise NotImplementedError()


class AsyncGeneration(Generic[P]):
    """A class for generating responses using LLMs asynchronously."""

    def __init__(self, fn: Callable[P, PromptTemplate[P]]) -> None:
        """Initializes an `AsyncGeneration` instance."""

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Response:
        """Generates a response using the LLM asynchronously."""
        raise NotImplementedError()

    async def stream(self, *args: P.args, **kwargs: P.kwargs) -> AsyncStream:
        """Generates a streaming response using the LLM asynchronously."""
        raise NotImplementedError()

    async def call_async(self, *args: P.args, **kwargs: P.kwargs) -> Response:
        """Generates an asynchronous response using the LLM."""
        return await self(*args, **kwargs)

    async def stream_async(self, *args: P.args, **kwargs: P.kwargs) -> AsyncStream:
        """Generates an asynchronous streaming response using the LLM."""
        return await self.stream(*args, **kwargs)


class StructuredGeneration(Generic[P, T]):
    """A class for generating structured responses using LLMs."""

    def __init__(self, fn: Callable[P, PromptTemplate[P]]) -> None:
        """Initializes a `StructuredGeneration` instance."""
        raise NotImplementedError()

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Response[T]:
        """Generates a structured response using the LLM."""
        raise NotImplementedError()

    def stream(self, *args: P.args, **kwargs: P.kwargs) -> StructuredStream[T]:
        """Generates a streaming structured response using the LLM."""
        raise NotImplementedError()

    async def call_async(self, *args: P.args, **kwargs: P.kwargs) -> Response[T]:
        """Generates an asynchronous structured response using the LLM."""
        raise NotImplementedError()

    async def stream_async(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStructuredStream[T]:
        """Generates an asynchronous streaming structured response using the LLM."""
        raise NotImplementedError()


class AsyncStructuredGeneration(Generic[P, T]):
    """A class for generating structured responses using LLMs asynchronously."""

    def __init__(self, fn: Callable[P, PromptTemplate[P]]) -> None:
        """Initializes an `AsyncStructuredGeneration` instance."""
        raise NotImplementedError()

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Response[T]:
        """Generates a structured response using the LLM asynchronously."""
        raise NotImplementedError()

    async def stream(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStructuredStream[T]:
        """Generates a streaming structured response using the LLM asynchronously."""
        raise NotImplementedError()

    async def call_async(self, *args: P.args, **kwargs: P.kwargs) -> Response[T]:
        """Generates an asynchronous structured response using the LLM."""
        return await self(*args, **kwargs)

    async def stream_async(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStructuredStream[T]:
        """Generates an asynchronous streaming structured response using the LLM."""
        return await self.stream(*args, **kwargs)


class GenerationDecorator(Protocol):
    """A decorator for generating responses using LLMs."""

    @overload
    def __call__(self, fn: AsyncPromptTemplate[P]) -> AsyncGeneration[P]:
        """Decorates an asynchronous function to generate responses using LLMs."""
        ...

    @overload
    def __call__(self, fn: PromptTemplate[P]) -> Generation[P]:
        """Decorates a synchronous function to generate responses using LLMs."""
        ...

    def __call__(
        self,
        fn: PromptTemplate[P] | AsyncPromptTemplate[P],
    ) -> Generation[P] | AsyncGeneration[P]:
        """Decorates a function to generate responses using LLMs."""
        raise NotImplementedError()


class StructuredGenerationDecorator(Protocol[T]):
    """A decorator for generating responses using LLMs."""

    @overload
    def __call__(self, fn: AsyncPromptTemplate[P]) -> AsyncStructuredGeneration[P, T]:
        """Decorates an asynchronous function to generate responses using LLMs."""
        ...

    @overload
    def __call__(self, fn: PromptTemplate[P]) -> StructuredGeneration[P, T]:
        """Decorates a synchronous function to generate responses using LLMs."""
        ...

    def __call__(
        self,
        fn: PromptTemplate[P] | AsyncPromptTemplate[P],
    ) -> StructuredGeneration[P, T] | AsyncStructuredGeneration[P, T]:
        """Decorates a function to generate responses using LLMs."""
        raise NotImplementedError()


@overload
def generate(
    model: ANTHROPIC_REGISTERED_LLMS,
    *,
    tools: Sequence[ToolDef] | None = None,
    response_format: None = None,
    client: AnthropicClient | None = None,
    **params: Unpack[AnthropicParams],
) -> GenerationDecorator:
    """Overload for Anthropic generation."""
    ...


@overload
def generate(
    model: ANTHROPIC_REGISTERED_LLMS,
    *,
    tools: Sequence[ToolDef] | None = None,
    response_format: ResponseFormat[T],
    client: AnthropicClient | None = None,
    **params: Unpack[AnthropicParams],
) -> StructuredGenerationDecorator[T]:
    """Overload for Anthropic structured generation."""
    ...


@overload
def generate(
    model: GOOGLE_REGISTERED_LLMS,
    *,
    tools: Sequence[ToolDef] | None = None,
    response_format: None = None,
    client: GoogleClient | None = None,
    **params: Unpack[GoogleParams],
) -> GenerationDecorator:
    """Overload for Google generation."""
    ...


@overload
def generate(
    model: GOOGLE_REGISTERED_LLMS,
    *,
    tools: Sequence[ToolDef] | None = None,
    response_format: ResponseFormat[T],
    client: GoogleClient | None = None,
    **params: Unpack[GoogleParams],
) -> StructuredGenerationDecorator[T]:
    """Overload for Google structured generation."""
    ...


@overload
def generate(
    model: OPENAI_REGISTERED_LLMS,
    *,
    tools: Sequence[ToolDef] | None = None,
    response_format: None = None,
    client: OpenAIClient | None = None,
    **params: Unpack[OpenAIParams],
) -> GenerationDecorator:
    """Overload for OpenAI generation."""
    ...


@overload
def generate(
    model: OPENAI_REGISTERED_LLMS,
    *,
    tools: Sequence[ToolDef] | None = None,
    response_format: ResponseFormat[T],
    client: OpenAIClient | None = None,
    **params: Unpack[OpenAIParams],
) -> StructuredGenerationDecorator[T]:
    """Overload for OpenAI structured generation."""
    ...


@overload
def generate(
    model: REGISTERED_LLMS,
    *,
    tools: Sequence[ToolDef] | None = None,
    response_format: None = None,
    client: Client | None = None,
    **params: Unpack[Params],
) -> GenerationDecorator:
    """Overload for all registered models so that autocomplete works."""
    ...


@overload
def generate(
    model: REGISTERED_LLMS,
    *,
    tools: Sequence[ToolDef] | None = None,
    response_format: ResponseFormat[T],
    client: Client | None = None,
    **params: Unpack[Params],
) -> StructuredGenerationDecorator[T]:
    """Overload for all registered models so that autocomplete works."""
    ...


def generate(
    model: REGISTERED_LLMS,
    *,
    tools: Sequence[ToolDef] | None = None,
    response_format: ResponseFormat[T] | None = None,
    client: Client | None = None,
    **params: Unpack[Params],
) -> GenerationDecorator | StructuredGenerationDecorator[T]:
    """Returns a decorator for turning prompt template functions into generations.

    Example:

        ```python
        from mirascope import llm

        @llm.generate("openai:gpt-4o-mini")
        def answer_question(question: str) -> str:
            return f"Answer this question: {question}"

        response: llm.Response = answer_question("What is the capital of France?")
        print(response.text)
        ```
    """
    raise NotImplementedError()
