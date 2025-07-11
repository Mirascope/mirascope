"""The `llm.call` decorator for turning `Prompt` functions into LLM calls."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Protocol, overload

from typing_extensions import Unpack

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
from .call import Call
from .context_call import ContextCall

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


from ..response_formatting import FormatT
from ..types import DepsT, P


class CallDecorator(Protocol[FormatT]):
    """A decorator for generating responses using LLMs."""

    @overload
    def __call__(
        self, fn: AsyncPrompt[P] | AsyncContextPrompt[P, None]
    ) -> AsyncCall[P, FormatT]:
        """Decorates an asynchronous function to generate responses using LLMs."""
        ...

    @overload
    def __call__(self, fn: Prompt[P] | ContextPrompt[P, None]) -> Call[P, FormatT]:
        """Decorates a synchronous function to generate responses using LLMs."""
        ...

    def __call__(
        self,
        fn: Prompt[P]
        | ContextPrompt[P, None]
        | AsyncPrompt[P]
        | AsyncContextPrompt[P, None],
    ) -> Call[P, FormatT] | AsyncCall[P, FormatT]:
        """Decorates a function to generate responses using LLMs."""
        ...


class ContextCallDecorator(Protocol[DepsT, FormatT]):
    """A decorator for generating responses using LLMs."""

    @overload
    def __call__(self, fn: AsyncContextPrompt[P, DepsT]) -> AsyncContextCall[P, DepsT, FormatT]:
        """Decorates an asynchronous function to generate responses using LLMs."""
        ...

    @overload
    def __call__(self, fn: ContextPrompt[P, DepsT]) -> ContextCall[P, DepsT, FormatT]:
        """Decorates a synchronous function to generate responses using LLMs."""
        ...

    def __call__(
        self,
        fn: ContextPrompt[P, DepsT] | AsyncContextPrompt[P, DepsT],
    ) -> ContextCall[P, DepsT, FormatT] | AsyncContextCall[P, DepsT, FormatT]:
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
) -> CallDecorator[None]:
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
) -> ContextCallDecorator[DepsT, None]:
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
) -> CallDecorator[FormatT]:
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
) -> ContextCallDecorator[DepsT, FormatT]:
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
) -> CallDecorator[None]:
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
) -> ContextCallDecorator[DepsT, None]:
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
) -> CallDecorator[FormatT]:
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
) -> ContextCallDecorator[DepsT, FormatT]:
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
) -> CallDecorator[None]:
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
) -> ContextCallDecorator[DepsT, None]:
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
) -> CallDecorator[FormatT]:
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
) -> ContextCallDecorator[DepsT, FormatT]:
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
) -> CallDecorator[None]:
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
) -> ContextCallDecorator[DepsT, None]:
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
) -> CallDecorator[FormatT]:
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
) -> ContextCallDecorator[DepsT, FormatT]:
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
    CallDecorator[None]
    | ContextCallDecorator[DepsT, None]
    | CallDecorator[FormatT]
    | ContextCallDecorator[DepsT, FormatT]
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
