"""The `llm.call` decorator for turning `Prompt` functions into LLM calls."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, overload

from typing_extensions import Unpack

from ..clients import (
    AnthropicClient,
    AnthropicParams,
    BaseClient,
    BaseParams,
    GoogleClient,
    GoogleParams,
    OpenAIClient,
    OpenAIParams,
)
from ..prompts import (
    AsyncContextPrompt,
    AsyncPrompt,
    ContextPrompt,
    Prompt,
)
from ..tools import (
    ContextToolT,
    ToolT,
)
from .call import AsyncCall, Call
from .context_call import AsyncContextCall, ContextCall

if TYPE_CHECKING:
    from ..clients import (
        ANTHROPIC_REGISTERED_LLMS,
        GOOGLE_REGISTERED_LLMS,
        OPENAI_REGISTERED_LLMS,
        REGISTERED_LLMS,
    )


from ..context import DepsT
from ..formatting import FormatT
from ..types import P


class CallDecorator(Protocol[ToolT, FormatT]):
    """A decorator for generating responses using LLMs."""

    @overload
    def __call__(
        self, fn: AsyncPrompt[P] | AsyncContextPrompt[P, None]
    ) -> AsyncCall[P, ToolT, FormatT]:
        """Decorates an asynchronous function to generate responses using LLMs."""
        ...

    @overload
    def __call__(
        self, fn: Prompt[P] | ContextPrompt[P, None]
    ) -> Call[P, ToolT, FormatT]:
        """Decorates a synchronous function to generate responses using LLMs."""
        ...

    def __call__(
        self,
        fn: Prompt[P]
        | ContextPrompt[P, None]
        | AsyncPrompt[P]
        | AsyncContextPrompt[P, None],
    ) -> Call[P, ToolT, FormatT] | AsyncCall[P, ToolT, FormatT]:
        """Decorates a function to generate responses using LLMs."""
        ...


class ContextCallDecorator(Protocol[ContextToolT, DepsT, FormatT]):
    """A decorator for generating responses using LLMs."""

    @overload
    def __call__(
        self, fn: AsyncContextPrompt[P, DepsT]
    ) -> AsyncContextCall[P, ContextToolT, DepsT, FormatT]:
        """Decorates an asynchronous function to generate responses using LLMs."""
        ...

    @overload
    def __call__(
        self, fn: ContextPrompt[P, DepsT]
    ) -> ContextCall[P, ContextToolT, DepsT, FormatT]:
        """Decorates a synchronous function to generate responses using LLMs."""
        ...

    def __call__(
        self,
        fn: ContextPrompt[P, DepsT] | AsyncContextPrompt[P, DepsT],
    ) -> (
        ContextCall[P, ContextToolT, DepsT, FormatT]
        | AsyncContextCall[P, ContextToolT, DepsT, FormatT]
    ):
        """Decorates a function to generate responses using LLMs."""
        ...


class AsyncCallDecorator(Protocol[ToolT, FormatT]):
    """A decorator for generating async responses using LLMs with async tools."""

    @overload
    def __call__(
        self, fn: AsyncPrompt[P] | AsyncContextPrompt[P, None]
    ) -> AsyncCall[P, ToolT, FormatT]:
        """Decorates an asynchronous function to generate responses using LLMs."""
        ...

    @overload
    def __call__(
        self, fn: Prompt[P] | ContextPrompt[P, None]
    ) -> AsyncCall[P, ToolT, FormatT]:
        """Decorates a synchronous function to generate async responses using LLMs."""
        ...

    def __call__(
        self,
        fn: Prompt[P]
        | ContextPrompt[P, None]
        | AsyncPrompt[P]
        | AsyncContextPrompt[P, None],
    ) -> AsyncCall[P, ToolT, FormatT]:
        """Decorates a function to generate async responses using LLMs."""
        ...


class AsyncContextCallDecorator(Protocol[ToolT, DepsT, FormatT]):
    """A decorator for generating async contextual responses using LLMs with async tools."""

    @overload
    def __call__(
        self, fn: AsyncContextPrompt[P, DepsT]
    ) -> AsyncContextCall[P, ToolT, DepsT, FormatT]:
        """Decorates an asynchronous function to generate responses using LLMs."""
        ...

    @overload
    def __call__(
        self, fn: ContextPrompt[P, DepsT]
    ) -> AsyncContextCall[P, ToolT, DepsT, FormatT]:
        """Decorates a synchronous function to generate async responses using LLMs."""
        ...

    def __call__(
        self,
        fn: ContextPrompt[P, DepsT] | AsyncContextPrompt[P, DepsT],
    ) -> AsyncContextCall[P, ToolT, DepsT, FormatT]:
        """Decorates a function to generate async responses using LLMs."""
        ...


@overload
def call(
    model: ANTHROPIC_REGISTERED_LLMS,
    *,
    tools: list[ToolT] | None = None,
    deps_type: type[None] | None = None,
    format: type[FormatT] | None = None,
    client: AnthropicClient | None = None,
    **params: Unpack[AnthropicParams],
) -> CallDecorator[ToolT, FormatT]:
    """Overload for Anthropic calls."""
    ...


@overload
def call(
    model: ANTHROPIC_REGISTERED_LLMS,
    *,
    tools: list[ToolT] | None = None,
    deps_type: type[DepsT],
    format: type[FormatT] | None = None,
    client: AnthropicClient | None = None,
    **params: Unpack[AnthropicParams],
) -> ContextCallDecorator[ToolT, DepsT, FormatT]:
    """Overload for Anthropic context calls."""
    ...


@overload
def call(
    model: GOOGLE_REGISTERED_LLMS,
    *,
    tools: list[ToolT] | None = None,
    deps_type: type[None] | None = None,
    format: type[FormatT] | None = None,
    client: GoogleClient | None = None,
    **params: Unpack[GoogleParams],
) -> CallDecorator[ToolT, FormatT]:
    """Overload for Google calls."""
    ...


@overload
def call(
    model: GOOGLE_REGISTERED_LLMS,
    *,
    tools: list[ToolT] | None = None,
    deps_type: type[DepsT],
    format: type[FormatT] | None = None,
    client: GoogleClient | None = None,
    **params: Unpack[GoogleParams],
) -> ContextCallDecorator[ToolT, DepsT, FormatT]:
    """Overload for Google context calls."""
    ...


@overload
def call(
    model: OPENAI_REGISTERED_LLMS,
    *,
    tools: list[ToolT] | None = None,
    deps_type: type[None] | None = None,
    format: type[FormatT] | None = None,
    client: OpenAIClient | None = None,
    **params: Unpack[OpenAIParams],
) -> CallDecorator[ToolT, FormatT]:
    """Overload for OpenAI calls."""
    ...


@overload
def call(
    model: OPENAI_REGISTERED_LLMS,
    *,
    tools: list[ToolT] | None = None,
    deps_type: type[DepsT],
    format: type[FormatT] | None = None,
    client: OpenAIClient | None = None,
    **params: Unpack[OpenAIParams],
) -> ContextCallDecorator[ToolT, DepsT, FormatT]:
    """Overload for OpenAI context calls."""
    ...


@overload
def call(
    model: REGISTERED_LLMS,
    *,
    deps_type: type[None] | None = None,
    tools: list[ToolT] | None = None,
    format: type[FormatT] | None = None,
    client: None = None,
    **params: Unpack[BaseParams],
) -> CallDecorator[ToolT, FormatT]:
    """Overload for all registered models with no deps."""
    ...


@overload
def call(
    model: REGISTERED_LLMS,
    *,
    tools: list[ContextToolT] | None = None,
    deps_type: type[DepsT],
    format: type[FormatT] | None = None,
    client: None = None,
    **params: Unpack[BaseParams],
) -> ContextCallDecorator[ContextToolT, DepsT, FormatT]:
    """Overload for all registered models with deps/context."""
    ...


def call(
    model: REGISTERED_LLMS,
    *,
    tools: list[ToolT] | list[ContextToolT] | None = None,
    deps_type: type[DepsT] | type[None] | None = None,
    format: type[FormatT] | None = None,
    client: BaseClient | None = None,
    **params: Unpack[BaseParams],
) -> CallDecorator[ToolT, FormatT] | ContextCallDecorator[ContextToolT, DepsT, FormatT]:
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
