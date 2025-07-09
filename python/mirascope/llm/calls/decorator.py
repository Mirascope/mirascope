"""The `llm.call` decorator for turning `Prompt` functions into LLM calls."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Protocol, overload

from typing_extensions import TypeVar, Unpack

from ..clients import BaseClient, BaseParams
from ..prompts import (
    AsyncContextPrompt,
    AsyncPrompt,
    ContextPrompt,
    Prompt,
)
from ..tools import ContextToolDef, ToolDef
from .async_call import AsyncCall
from .async_context_call import AsyncContextCall
from .async_structured_call import AsyncStructuredCall
from .async_structured_context_call import AsyncStructuredContextCall
from .call import Call
from .context_call import ContextCall
from .structured_call import StructuredCall
from .structured_context_call import StructuredContextCall

if TYPE_CHECKING:
    from ..clients import (
        ANTHROPIC_REGISTERED_LLMS,
        GOOGLE_REGISTERED_LLMS,
        OPENAI_REGISTERED_LLMS,
        REGISTERED_LLMS,
        AnthropicClient,
        AnthropicParams,
        GoogleClient,
        GoogleParams,
        OpenAIClient,
        OpenAIParams,
    )


from ..types import DepsT, FormatT, P

NoneType = type(None)


NoDepsT = TypeVar("NoDepsT", bound=None)


class CallDecorator(Protocol):
    """A decorator for generating responses using LLMs."""

    @overload
    def __call__(
        self, fn: AsyncPrompt[P] | AsyncContextPrompt[P, NoDepsT]
    ) -> AsyncCall[P]:
        """Decorates an asynchronous function to generate responses using LLMs."""
        ...

    @overload
    def __call__(self, fn: Prompt[P] | ContextPrompt[P, NoDepsT]) -> Call[P]:
        """Decorates a synchronous function to generate responses using LLMs."""
        ...

    def __call__(
        self,
        fn: Prompt[P]
        | ContextPrompt[P, NoDepsT]
        | AsyncPrompt[P]
        | AsyncContextPrompt[P, NoDepsT],
    ) -> Call[P] | AsyncCall[P]:
        """Decorates a function to generate responses using LLMs."""
        ...


class ContextCallDecorator(Protocol[DepsT]):
    """A decorator for generating responses using LLMs."""

    @overload
    def __call__(self, fn: AsyncContextPrompt[P, DepsT]) -> AsyncContextCall[P, DepsT]:
        """Decorates an asynchronous function to generate responses using LLMs."""
        ...

    @overload
    def __call__(self, fn: ContextPrompt[P, DepsT]) -> ContextCall[P, DepsT]:
        """Decorates a synchronous function to generate responses using LLMs."""
        ...

    def __call__(
        self,
        fn: ContextPrompt[P, DepsT] | AsyncContextPrompt[P, DepsT],
    ) -> ContextCall[P, DepsT] | AsyncContextCall[P, DepsT]:
        """Decorates a function to generate responses using LLMs."""
        ...


class StructuredCallDecorator(Protocol[FormatT]):
    """A decorator for generating responses using LLMs."""

    @overload
    def __call__(self, fn: AsyncPrompt[P]) -> AsyncStructuredCall[P, FormatT]:
        """Decorates an asynchronous function to generate responses using LLMs."""
        ...

    @overload
    def __call__(self, fn: Prompt[P]) -> StructuredCall[P, FormatT]:
        """Decorates a synchronous function to generate responses using LLMs."""
        ...

    def __call__(
        self, fn: Prompt[P] | AsyncPrompt[P]
    ) -> StructuredCall[P, FormatT] | AsyncStructuredCall[P, FormatT]:
        """Decorates a function to generate responses using LLMs."""
        ...


class StructuredContextCallDecorator(Protocol[FormatT, DepsT]):
    """A decorator for generating responses using LLMs."""

    @overload
    def __call__(
        self, fn: AsyncContextPrompt[P, DepsT]
    ) -> AsyncStructuredContextCall[P, FormatT, DepsT]:
        """Decorates an asynchronous function to generate responses using LLMs."""
        ...

    @overload
    def __call__(
        self, fn: ContextPrompt[P, DepsT]
    ) -> StructuredContextCall[P, FormatT, DepsT]:
        """Decorates a synchronous function to generate responses using LLMs."""
        ...

    def __call__(
        self,
        fn: ContextPrompt[P, DepsT] | AsyncContextPrompt[P, DepsT],
    ) -> (
        StructuredContextCall[P, FormatT, DepsT]
        | AsyncStructuredContextCall[P, FormatT, DepsT]
    ):
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
    response_format: type[FormatT],
    client: AnthropicClient | None = None,
    **params: Unpack[AnthropicParams],
) -> StructuredCallDecorator[FormatT]:
    """Overload for Anthropic structured generation."""
    ...


@overload
def call(
    model: ANTHROPIC_REGISTERED_LLMS,
    *,
    deps_type: type[DepsT],
    tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]] | None = None,
    response_format: type[FormatT],
    client: AnthropicClient | None = None,
    **params: Unpack[AnthropicParams],
) -> StructuredContextCallDecorator[FormatT, DepsT]:
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
    response_format: type[FormatT],
    client: GoogleClient | None = None,
    **params: Unpack[GoogleParams],
) -> StructuredCallDecorator[FormatT]:
    """Overload for Google structured generation."""
    ...


@overload
def call(
    model: GOOGLE_REGISTERED_LLMS,
    *,
    deps_type: type[DepsT],
    tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]] | None = None,
    response_format: type[FormatT],
    client: GoogleClient | None = None,
    **params: Unpack[GoogleParams],
) -> StructuredContextCallDecorator[FormatT, DepsT]:
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
    response_format: type[FormatT],
    client: OpenAIClient | None = None,
    **params: Unpack[OpenAIParams],
) -> StructuredCallDecorator[FormatT]:
    """Overload for OpenAI structured generation."""
    ...


@overload
def call(
    model: OPENAI_REGISTERED_LLMS,
    *,
    deps_type: type[DepsT],
    tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]] | None = None,
    response_format: type[FormatT],
    client: OpenAIClient | None = None,
    **params: Unpack[OpenAIParams],
) -> StructuredContextCallDecorator[FormatT, DepsT]:
    """Overload for OpenAI structured contextual generation."""
    ...


@overload
def call(
    model: REGISTERED_LLMS,
    *,
    deps_type: type[None] | None = None,
    tools: Sequence[ToolDef] | None = None,
    response_format: None = None,
    client: None,
    **params: Unpack[BaseParams],
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
    client: None,
    **params: Unpack[BaseParams],
) -> ContextCallDecorator[DepsT]:
    """Overload for all registered models so that autocomplete works."""
    ...


@overload
def call(
    model: REGISTERED_LLMS,
    *,
    deps_type: type[None] | None = None,
    tools: Sequence[ToolDef] | None = None,
    response_format: type[FormatT],
    client: None,
    **params: Unpack[BaseParams],
) -> StructuredCallDecorator[FormatT]:
    """Overload for all registered models so that autocomplete works."""
    ...


@overload
def call(
    model: REGISTERED_LLMS,
    *,
    deps_type: type[DepsT],
    tools: Sequence[ToolDef | ContextToolDef[..., Any, DepsT]] | None = None,
    response_format: type[FormatT],
    client: None,
    **params: Unpack[BaseParams],
) -> StructuredContextCallDecorator[FormatT, DepsT]:
    """Overload for all registered models so that autocomplete works."""
    ...


def call(
    model: REGISTERED_LLMS,
    *,
    deps_type: type[DepsT] | type[None] | None = None,
    tools: Sequence[ToolDef]
    | Sequence[ToolDef | ContextToolDef[..., Any, DepsT]]
    | None = None,
    response_format: type[FormatT] | None = None,
    client: BaseClient | None = None,
    **params: Unpack[BaseParams],
) -> (
    CallDecorator
    | ContextCallDecorator[DepsT]
    | StructuredCallDecorator[FormatT]
    | StructuredContextCallDecorator[FormatT, DepsT]
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
