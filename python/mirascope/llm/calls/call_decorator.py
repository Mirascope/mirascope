"""The `llm.call` decorator for turning `Prompt` functions into LLM calls."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Protocol, overload

from typing_extensions import Unpack

from ..prompts import (
    AsyncPrompt,
    Prompt,
)
from ..tools import (
    ToolT,
)
from .call import AsyncCall, Call

if TYPE_CHECKING:
    from ..clients import (
        AnthropicClient,
        AnthropicModel,
        AnthropicParams,
        BaseClient,
        BaseParams,
        GoogleClient,
        GoogleModel,
        GoogleParams,
        Model,
        OpenAIClient,
        OpenAIModel,
        OpenAIParams,
        Provider,
    )


from ..formatting import FormatT
from ..types import P


class CallDecorator(Protocol[ToolT, FormatT]):
    """A decorator for converting prompts to calls."""

    @overload
    def __call__(self, fn: AsyncPrompt[P]) -> AsyncCall[P, ToolT, FormatT]:
        """Decorate an async prompt into an AsyncCall."""
        ...

    @overload
    def __call__(self, fn: Prompt[P]) -> Call[P, ToolT, FormatT]:
        """Decorate a prompt into a Call."""
        ...

    def __call__(
        self, fn: Prompt[P] | AsyncPrompt[P]
    ) -> Call[P, ToolT, FormatT] | AsyncCall[P, ToolT, FormatT]:
        """Decorates a prompt into a Call."""
        raise NotImplementedError()


@overload
def call(
    *,
    provider: Literal["anthropic"],
    model: AnthropicModel,
    tools: list[ToolT] | None = None,
    format: type[FormatT] | None = None,
    client: AnthropicClient | None = None,
    **params: Unpack[AnthropicParams],
) -> CallDecorator[ToolT, FormatT]:
    """Decorate a prompt into a Call using Anthropic models."""
    ...


@overload
def call(
    *,
    provider: Literal["google"],
    model: GoogleModel,
    tools: list[ToolT] | None = None,
    format: type[FormatT] | None = None,
    client: GoogleClient | None = None,
    **params: Unpack[GoogleParams],
) -> CallDecorator[ToolT, FormatT]:
    """Decorate a prompt into a Call using Google models."""
    ...


@overload
def call(
    *,
    provider: Literal["openai"],
    model: OpenAIModel,
    tools: list[ToolT] | None = None,
    format: type[FormatT] | None = None,
    client: OpenAIClient | None = None,
    **params: Unpack[OpenAIParams],
) -> CallDecorator[ToolT, FormatT]:
    """Decorate a prompt into a Call using OpenAI models."""
    ...


@overload
def call(
    *,
    provider: Provider,
    model: Model,
    tools: list[ToolT] | None = None,
    format: type[FormatT] | None = None,
    client: None = None,
    **params: Unpack[BaseParams],
) -> CallDecorator[ToolT, FormatT]:
    """Decorate a prompt into a Call using any registered model."""
    ...


def call(
    *,
    provider: Provider,
    model: Model,
    tools: list[ToolT] | None = None,
    format: type[FormatT] | None = None,
    client: BaseClient | None = None,
    **params: Unpack[BaseParams],
) -> CallDecorator[ToolT, FormatT]:
    """Returns a decorator for turning prompt template functions into generations.

    Example:

        ```python
        from mirascope import llm

        @llm.call(
            provider="openai",
            model="gpt-4o-mini",
        )
        def answer_question(question: str) -> str:
            return f"Answer this question: {question}"

        response: llm.Response = answer_question("What is the capital of France?")
        print(response)
        ```
    """
    raise NotImplementedError()
