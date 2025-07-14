"""The `llm.call` decorator for turning `Prompt` functions into LLM calls."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Protocol, overload

from typing_extensions import Unpack

from ..clients import BaseClient, BaseParams
from ..prompts import (
    AsyncContextPrompt,
    AsyncPrompt,
    ContextPrompt,
    Prompt,
)
from ..tools import AsyncContextTool, AsyncTool, ContextTool, Tool
from ..types import Jsonable
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


from ..context import DepsT
from ..response_formatting import FormatT
from ..types import P


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
    def __call__(
        self, fn: AsyncContextPrompt[P, DepsT]
    ) -> AsyncContextCall[P, DepsT, FormatT]:
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


class AsyncCallDecorator(Protocol[FormatT]):
    """A decorator for generating async responses using LLMs with async tools."""

    @overload
    def __call__(
        self, fn: AsyncPrompt[P] | AsyncContextPrompt[P, None]
    ) -> AsyncCall[P, FormatT]:
        """Decorates an asynchronous function to generate responses using LLMs."""
        ...

    @overload
    def __call__(self, fn: Prompt[P] | ContextPrompt[P, None]) -> AsyncCall[P, FormatT]:
        """Decorates a synchronous function to generate async responses using LLMs."""
        ...

    def __call__(
        self,
        fn: Prompt[P]
        | ContextPrompt[P, None]
        | AsyncPrompt[P]
        | AsyncContextPrompt[P, None],
    ) -> AsyncCall[P, FormatT]:
        """Decorates a function to generate async responses using LLMs."""
        ...


class AsyncContextCallDecorator(Protocol[DepsT, FormatT]):
    """A decorator for generating async contextual responses using LLMs with async tools."""

    @overload
    def __call__(
        self, fn: AsyncContextPrompt[P, DepsT]
    ) -> AsyncContextCall[P, DepsT, FormatT]:
        """Decorates an asynchronous function to generate responses using LLMs."""
        ...

    @overload
    def __call__(
        self, fn: ContextPrompt[P, DepsT]
    ) -> AsyncContextCall[P, DepsT, FormatT]:
        """Decorates a synchronous function to generate async responses using LLMs."""
        ...

    def __call__(
        self,
        fn: ContextPrompt[P, DepsT] | AsyncContextPrompt[P, DepsT],
    ) -> AsyncContextCall[P, DepsT, FormatT]:
        """Decorates a function to generate async responses using LLMs."""
        ...


@overload
def call(
    model: ANTHROPIC_REGISTERED_LLMS,
    *,
    deps_type: type[None] | None = None,
    tools: Sequence[Tool] | None = None,
    response_format: type[FormatT] | None = None,
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
    tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]] | None = None,
    response_format: type[FormatT] | None = None,
    client: AnthropicClient | None = None,
    **params: Unpack[AnthropicParams],
) -> ContextCallDecorator[DepsT, FormatT]:
    """Overload for Anthropic structured contextual generation."""
    ...


@overload
def call(
    model: ANTHROPIC_REGISTERED_LLMS,
    *,
    deps_type: type[None] | None = None,
    tools: Sequence[AsyncTool],
    response_format: type[FormatT] | None = None,
    client: AnthropicClient | None = None,
    **params: Unpack[AnthropicParams],
) -> AsyncCallDecorator[FormatT]:
    """Overload for Anthropic generation with async tools."""
    ...


@overload
def call(
    model: ANTHROPIC_REGISTERED_LLMS,
    *,
    deps_type: type[DepsT],
    tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
    response_format: type[FormatT] | None = None,
    client: AnthropicClient | None = None,
    **params: Unpack[AnthropicParams],
) -> AsyncContextCallDecorator[DepsT, FormatT]:
    """Overload for Anthropic contextual generation with async tools."""
    ...


@overload
def call(
    model: GOOGLE_REGISTERED_LLMS,
    *,
    deps_type: type[None] | None = None,
    tools: Sequence[Tool] | None = None,
    response_format: type[FormatT] | None = None,
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
    tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]] | None = None,
    response_format: type[FormatT] | None = None,
    client: GoogleClient | None = None,
    **params: Unpack[GoogleParams],
) -> ContextCallDecorator[DepsT, FormatT]:
    """Overload for Google structured contextual generation."""
    ...


@overload
def call(
    model: GOOGLE_REGISTERED_LLMS,
    *,
    deps_type: type[None] | None = None,
    tools: Sequence[AsyncTool],
    response_format: type[FormatT] | None = None,
    client: GoogleClient | None = None,
    **params: Unpack[GoogleParams],
) -> AsyncCallDecorator[FormatT]:
    """Overload for Google generation with async tools."""
    ...


@overload
def call(
    model: GOOGLE_REGISTERED_LLMS,
    *,
    deps_type: type[DepsT],
    tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
    response_format: type[FormatT] | None = None,
    client: GoogleClient | None = None,
    **params: Unpack[GoogleParams],
) -> AsyncContextCallDecorator[DepsT, FormatT]:
    """Overload for Google contextual generation with async tools."""
    ...


@overload
def call(
    model: OPENAI_REGISTERED_LLMS,
    *,
    deps_type: type[None] | None = None,
    tools: Sequence[Tool] | None = None,
    response_format: type[FormatT] | None = None,
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
    tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]] | None = None,
    response_format: type[FormatT] | None = None,
    client: OpenAIClient | None = None,
    **params: Unpack[OpenAIParams],
) -> ContextCallDecorator[DepsT, FormatT]:
    """Overload for OpenAI structured contextual generation."""
    ...


@overload
def call(
    model: OPENAI_REGISTERED_LLMS,
    *,
    deps_type: type[None] | None = None,
    tools: Sequence[AsyncTool],
    response_format: type[FormatT] | None = None,
    client: OpenAIClient | None = None,
    **params: Unpack[OpenAIParams],
) -> AsyncCallDecorator[FormatT]:
    """Overload for OpenAI generation with async tools."""
    ...


@overload
def call(
    model: OPENAI_REGISTERED_LLMS,
    *,
    deps_type: type[DepsT],
    tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
    response_format: type[FormatT] | None = None,
    client: OpenAIClient | None = None,
    **params: Unpack[OpenAIParams],
) -> AsyncContextCallDecorator[DepsT, FormatT]:
    """Overload for OpenAI contextual generation with async tools."""
    ...


@overload
def call(
    model: REGISTERED_LLMS,
    *,
    deps_type: type[None] | None = None,
    tools: Sequence[Tool] | None = None,
    response_format: type[FormatT] | None = None,
    client: None,
    **params: Unpack[BaseParams],
) -> CallDecorator[FormatT]:
    """Overload for all registered models so that autocomplete works."""
    ...


@overload
def call(
    model: REGISTERED_LLMS,
    *,
    deps_type: type[None] | None = None,
    tools: Sequence[AsyncTool],
    response_format: type[FormatT] | None = None,
    client: None,
    **params: Unpack[BaseParams],
) -> AsyncCallDecorator[FormatT]:
    """Overload for all registered models with async tools."""
    ...


@overload
def call(
    model: REGISTERED_LLMS,
    *,
    deps_type: type[DepsT],
    tools: Sequence[Tool | ContextTool[..., Jsonable, DepsT]] | None = None,
    response_format: type[FormatT] | None = None,
    client: None,
    **params: Unpack[BaseParams],
) -> ContextCallDecorator[DepsT, FormatT]:
    """Overload for all registered models so that autocomplete works."""
    ...


@overload
def call(
    model: REGISTERED_LLMS,
    *,
    deps_type: type[DepsT],
    tools: Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]],
    response_format: type[FormatT] | None = None,
    client: None,
    **params: Unpack[BaseParams],
) -> AsyncContextCallDecorator[DepsT, FormatT]:
    """Overload for all registered models with async context tools."""
    ...


def call(
    model: REGISTERED_LLMS,
    *,
    deps_type: type[DepsT] | type[None] | None = None,
    tools: Sequence[Tool]
    | Sequence[Tool | ContextTool[..., Jsonable, DepsT]]
    | Sequence[AsyncTool]
    | Sequence[AsyncTool | AsyncContextTool[..., Jsonable, DepsT]]
    | None = None,
    response_format: type[FormatT] | None = None,
    client: BaseClient | None = None,
    **params: Unpack[BaseParams],
) -> (
    CallDecorator[None]
    | ContextCallDecorator[DepsT, None]
    | CallDecorator[FormatT]
    | ContextCallDecorator[DepsT, FormatT]
    | AsyncCallDecorator[None]
    | AsyncContextCallDecorator[DepsT, None]
    | AsyncCallDecorator[FormatT]
    | AsyncContextCallDecorator[DepsT, FormatT]
):
    """Returns a decorator for turning prompt template functions into generations.

    Example:

        ```python
        from mirascope import llm

        @llm.call("openai:gpt-4o-mini")
        def answer_question(question: str) -> str:
            return f"Answer this question: {question}"

        response: llm.Response = answer_question("What is the capital of France?")
        print(response)
        ```
    """
    raise NotImplementedError()
