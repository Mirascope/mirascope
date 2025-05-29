"""The `llm.call` decorator for turning `PromptTemplate` functions into LLM calls."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, ParamSpec, Protocol, overload

from typing_extensions import TypeVar, Unpack

from ..models import Client, Params
from ..prompt_templates import (
    AsyncContextPromptTemplate,
    AsyncPromptTemplate,
    ContextPromptTemplate,
    PromptTemplate,
)
from ..tools import ContextToolDef, ToolDef
from ..types import Dataclass
from .async_call import AsyncCall
from .async_context_call import AsyncContextCall
from .async_structured_call import AsyncStructuredCall
from .async_structured_context_call import AsyncStructuredContextCall
from .call import Call
from .context_call import ContextCall
from .structured_call import StructuredCall
from .structured_context_call import StructuredContextCall

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

NoneType = type(None)
P = ParamSpec("P")
T = TypeVar("T", bound=Dataclass | None, default=None)
DepsT = TypeVar("DepsT", default=None)
NoDepsT = TypeVar("NoDepsT", bound=None)


class CallDecorator(Protocol):
    """A decorator for generating responses using LLMs."""

    @overload
    def __call__(
        self, fn: AsyncPromptTemplate[P] | AsyncContextPromptTemplate[P, NoDepsT]
    ) -> AsyncCall[P]:
        """Decorates an asynchronous function to generate responses using LLMs."""
        ...

    @overload
    def __call__(
        self, fn: PromptTemplate[P] | ContextPromptTemplate[P, NoDepsT]
    ) -> Call[P]:
        """Decorates a synchronous function to generate responses using LLMs."""
        ...

    def __call__(
        self,
        fn: PromptTemplate[P]
        | ContextPromptTemplate[P, NoDepsT]
        | AsyncPromptTemplate[P]
        | AsyncContextPromptTemplate[P, NoDepsT],
    ) -> Call[P] | AsyncCall[P]:
        """Decorates a function to generate responses using LLMs."""
        ...


class ContextCallDecorator(Protocol[DepsT]):
    """A decorator for generating responses using LLMs."""

    @overload
    def __call__(
        self, fn: AsyncContextPromptTemplate[P, DepsT]
    ) -> AsyncContextCall[P, DepsT]:
        """Decorates an asynchronous function to generate responses using LLMs."""
        ...

    @overload
    def __call__(self, fn: ContextPromptTemplate[P, DepsT]) -> ContextCall[P, DepsT]:
        """Decorates a synchronous function to generate responses using LLMs."""
        ...

    def __call__(
        self,
        fn: ContextPromptTemplate[P, DepsT] | AsyncContextPromptTemplate[P, DepsT],
    ) -> ContextCall[P, DepsT] | AsyncContextCall[P, DepsT]:
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
        self, fn: PromptTemplate[P] | AsyncPromptTemplate[P]
    ) -> StructuredCall[P, T] | AsyncStructuredCall[P, T]:
        """Decorates a function to generate responses using LLMs."""
        ...


class StructuredContextCallDecorator(Protocol[T, DepsT]):
    """A decorator for generating responses using LLMs."""

    @overload
    def __call__(
        self, fn: AsyncContextPromptTemplate[P, DepsT]
    ) -> AsyncStructuredContextCall[P, T, DepsT]:
        """Decorates an asynchronous function to generate responses using LLMs."""
        ...

    @overload
    def __call__(
        self, fn: ContextPromptTemplate[P, DepsT]
    ) -> StructuredContextCall[P, T, DepsT]:
        """Decorates a synchronous function to generate responses using LLMs."""
        ...

    def __call__(
        self,
        fn: ContextPromptTemplate[P, DepsT] | AsyncContextPromptTemplate[P, DepsT],
    ) -> StructuredContextCall[P, T, DepsT] | AsyncStructuredContextCall[P, T, DepsT]:
        """Decorates a function to generate responses using LLMs."""
        ...


@overload
def call(
    model: ANTHROPIC_REGISTERED_LLMS,
    *,
    deps_type: type[None] | None = None,
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
    deps_type: type[DepsT],
    tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]] | None = None,
    response_format: None = None,
    client: AnthropicClient | None = None,
    **params: Unpack[AnthropicParams],
) -> ContextCallDecorator[DepsT]:
    """Overload for Anthropic contextual generation."""
    ...


@overload
def call(
    model: ANTHROPIC_REGISTERED_LLMS,
    *,
    deps_type: type[None] | None = None,
    tools: Sequence[ToolDef] | None = None,
    response_format: type[T],
    client: AnthropicClient | None = None,
    **params: Unpack[AnthropicParams],
) -> StructuredCallDecorator[T]:
    """Overload for Anthropic structured generation."""
    ...


@overload
def call(
    model: ANTHROPIC_REGISTERED_LLMS,
    *,
    deps_type: type[DepsT],
    tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]] | None = None,
    response_format: type[T],
    client: AnthropicClient | None = None,
    **params: Unpack[AnthropicParams],
) -> StructuredContextCallDecorator[T, DepsT]:
    """Overload for Anthropic structured contextual generation."""
    ...


@overload
def call(
    model: GOOGLE_REGISTERED_LLMS,
    *,
    deps_type: type[None] | None = None,
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
    deps_type: type[DepsT],
    tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]] | None = None,
    response_format: None = None,
    client: GoogleClient | None = None,
    **params: Unpack[GoogleParams],
) -> ContextCallDecorator[DepsT]:
    """Overload for Google contextual generation."""
    ...


@overload
def call(
    model: GOOGLE_REGISTERED_LLMS,
    *,
    deps_type: type[None] | None = None,
    tools: Sequence[ToolDef] | None = None,
    response_format: type[T],
    client: GoogleClient | None = None,
    **params: Unpack[GoogleParams],
) -> StructuredCallDecorator[T]:
    """Overload for Google structured generation."""
    ...


@overload
def call(
    model: GOOGLE_REGISTERED_LLMS,
    *,
    deps_type: type[DepsT],
    tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]] | None = None,
    response_format: type[T],
    client: GoogleClient | None = None,
    **params: Unpack[GoogleParams],
) -> StructuredContextCallDecorator[T, DepsT]:
    """Overload for Google structured contextual generation."""
    ...


@overload
def call(
    model: OPENAI_REGISTERED_LLMS,
    *,
    deps_type: type[None] | None = None,
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
    deps_type: type[DepsT],
    tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]] | None = None,
    response_format: None = None,
    client: OpenAIClient | None = None,
    **params: Unpack[OpenAIParams],
) -> ContextCallDecorator[DepsT]:
    """Overload for OpenAI contextual generation."""
    ...


@overload
def call(
    model: OPENAI_REGISTERED_LLMS,
    *,
    deps_type: type[None] | None = None,
    tools: Sequence[ToolDef] | None = None,
    response_format: type[T],
    client: OpenAIClient | None = None,
    **params: Unpack[OpenAIParams],
) -> StructuredCallDecorator[T]:
    """Overload for OpenAI structured generation."""
    ...


@overload
def call(
    model: OPENAI_REGISTERED_LLMS,
    *,
    deps_type: type[DepsT],
    tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]] | None = None,
    response_format: type[T],
    client: OpenAIClient | None = None,
    **params: Unpack[OpenAIParams],
) -> StructuredContextCallDecorator[T, DepsT]:
    """Overload for OpenAI structured contextual generation."""
    ...


@overload
def call(
    model: REGISTERED_LLMS,
    *,
    deps_type: type[None] | None = None,
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
    deps_type: type[DepsT],
    tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]] | None = None,
    response_format: None = None,
    client: Client | None = None,
    **params: Unpack[Params],
) -> ContextCallDecorator[DepsT]:
    """Overload for all registered models so that autocomplete works."""
    ...


@overload
def call(
    model: REGISTERED_LLMS,
    *,
    deps_type: type[None] | None = None,
    tools: Sequence[ToolDef] | None = None,
    response_format: type[T],
    client: Client | None = None,
    **params: Unpack[Params],
) -> StructuredCallDecorator[T]:
    """Overload for all registered models so that autocomplete works."""
    ...


@overload
def call(
    model: REGISTERED_LLMS,
    *,
    deps_type: type[DepsT],
    tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]] | None = None,
    response_format: type[T],
    client: Client | None = None,
    **params: Unpack[Params],
) -> StructuredContextCallDecorator[T, DepsT]:
    """Overload for all registered models so that autocomplete works."""
    ...


def call(
    model: REGISTERED_LLMS,
    *,
    deps_type: type[DepsT] | type[None] | None = None,
    tools: Sequence[ToolDef]
    | Sequence[ToolDef | ContextToolDef[..., Any, DepsT]]
    | None = None,
    response_format: type[T] | None = None,
    client: Client | None = None,
    **params: Unpack[Params],
) -> (
    CallDecorator
    | ContextCallDecorator[DepsT]
    | StructuredCallDecorator[T]
    | StructuredContextCallDecorator[T, DepsT]
):
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
