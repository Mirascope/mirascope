"""The `llm.call` decorator for turning `PromptTemplate` functions into LLM calls."""

from collections.abc import Sequence
from typing import TYPE_CHECKING, ParamSpec, Protocol, overload

from typing_extensions import TypeVar, Unpack

from ..messages import AsyncPromptTemplate, PromptTemplate
from ..models import Client, Params
from ..response_formatting import ResponseFormat
from ..tools import ToolDef
from .async_call import AsyncCall
from .call import Call
from .structured_call import AsyncStructuredCall, StructuredCall

if TYPE_CHECKING:
    from ..models import (
        ANTHROPIC_REGISTERED_LLMS,
        GOOGLE_REGISTERED_LLMS,
        OPENAI_REGISTERED_LLMS,
        REGISTERED_LLMS,
    )
    from ..models.anthropic import AnthropicClient, AnthropicParams
    from ..models.google import GoogleClient, GoogleParams
    from ..models.openai import OpenAIClient, OpenAIParams

P = ParamSpec("P")
T = TypeVar("T", default=None)


class CallDecorator(Protocol):
    """A decorator for generating responses using LLMs."""

    @overload
    def __call__(self, fn: AsyncPromptTemplate[P]) -> AsyncCall[P]:
        """Decorates an asynchronous function to generate responses using LLMs."""
        ...

    @overload
    def __call__(self, fn: PromptTemplate[P]) -> Call[P]:
        """Decorates a synchronous function to generate responses using LLMs."""
        ...

    def __call__(
        self,
        fn: PromptTemplate[P] | AsyncPromptTemplate[P],
    ) -> Call[P] | AsyncCall[P]:
        """Decorates a function to generate responses using LLMs."""
        ...


class StructuredCallDecorator(Protocol[T]):
    """A decorator for generating responses using LLMs."""

    @overload
    def __call__(self, fn: AsyncPromptTemplate[P]) -> AsyncStructuredCall[P, T]:
        """Decorates an asynchronous function to generate responses using LLMs."""
        ...

    @overload
    def __call__(self, fn: PromptTemplate[P]) -> StructuredCall[P, T]:
        """Decorates a synchronous function to generate responses using LLMs."""
        ...

    def __call__(
        self,
        fn: PromptTemplate[P] | AsyncPromptTemplate[P],
    ) -> StructuredCall[P, T] | AsyncStructuredCall[P, T]:
        """Decorates a function to generate responses using LLMs."""
        ...


@overload
def call(
    model: ANTHROPIC_REGISTERED_LLMS,
    *,
    tools: Sequence[ToolDef] | None = None,
    response_format: None = None,
    client: AnthropicClient | None = None,
    **params: Unpack[AnthropicParams],
) -> CallDecorator:
    """Overload for Anthropic generation."""
    ...


@overload
def call(
    model: ANTHROPIC_REGISTERED_LLMS,
    *,
    tools: Sequence[ToolDef] | None = None,
    response_format: ResponseFormat[T],
    client: AnthropicClient | None = None,
    **params: Unpack[AnthropicParams],
) -> StructuredCallDecorator[T]:
    """Overload for Anthropic structured generation."""
    ...


@overload
def call(
    model: GOOGLE_REGISTERED_LLMS,
    *,
    tools: Sequence[ToolDef] | None = None,
    response_format: None = None,
    client: GoogleClient | None = None,
    **params: Unpack[GoogleParams],
) -> CallDecorator:
    """Overload for Google generation."""
    ...


@overload
def call(
    model: GOOGLE_REGISTERED_LLMS,
    *,
    tools: Sequence[ToolDef] | None = None,
    response_format: ResponseFormat[T],
    client: GoogleClient | None = None,
    **params: Unpack[GoogleParams],
) -> StructuredCallDecorator[T]:
    """Overload for Google structured generation."""
    ...


@overload
def call(
    model: OPENAI_REGISTERED_LLMS,
    *,
    tools: Sequence[ToolDef] | None = None,
    response_format: None = None,
    client: OpenAIClient | None = None,
    **params: Unpack[OpenAIParams],
) -> CallDecorator:
    """Overload for OpenAI generation."""
    ...


@overload
def call(
    model: OPENAI_REGISTERED_LLMS,
    *,
    tools: Sequence[ToolDef] | None = None,
    response_format: ResponseFormat[T],
    client: OpenAIClient | None = None,
    **params: Unpack[OpenAIParams],
) -> StructuredCallDecorator[T]:
    """Overload for OpenAI structured generation."""
    ...


@overload
def call(
    model: REGISTERED_LLMS,
    *,
    tools: Sequence[ToolDef] | None = None,
    response_format: None = None,
    client: Client | None = None,
    **params: Unpack[Params],
) -> CallDecorator:
    """Overload for all registered models so that autocomplete works."""
    ...


@overload
def call(
    model: REGISTERED_LLMS,
    *,
    tools: Sequence[ToolDef] | None = None,
    response_format: ResponseFormat[T],
    client: Client | None = None,
    **params: Unpack[Params],
) -> StructuredCallDecorator[T]:
    """Overload for all registered models so that autocomplete works."""
    ...


def call(
    model: REGISTERED_LLMS,
    *,
    tools: Sequence[ToolDef] | None = None,
    response_format: ResponseFormat[T] | None = None,
    client: Client | None = None,
    **params: Unpack[Params],
) -> CallDecorator | StructuredCallDecorator[T]:
    """Returns a decorator for turning prompt template functions into generations.

    Example:

        ```python
        from mirascope import llm

        @llm.call("openai:gpt-4o-mini")
        def answer_question(question: str) -> str:
            return f"Answer this question: {question}"

        response: llm.Response = answer_question("What is the capital of France?")
        print(response.text)
        ```
    """
    raise NotImplementedError()
