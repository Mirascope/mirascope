"""The `llm.call` decorator for turning `Prompt` functions into LLM calls."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, Literal, cast, overload

from typing_extensions import Unpack

from ..models import LLM
from ..prompts import AsyncPrompt, Prompt
from ..prompts import _utils as _prompt_utils
from ..tools import AsyncTool, Tool, ToolT
from . import _utils
from .call import AsyncCall, Call

if TYPE_CHECKING:
    from ..clients import (
        AnthropicClient,
        AnthropicModel,
        AnthropicParams,
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
from ..tools import AsyncToolkit, Toolkit
from ..types import P


@dataclass(kw_only=True)
class CallDecorator(Generic[ToolT, FormatT]):
    """A decorator for converting prompts to calls."""

    model: LLM
    tools: Sequence[ToolT] | None
    format: type[FormatT] | None

    @overload
    def __call__(
        self: CallDecorator[AsyncTool, FormatT], fn: AsyncPrompt[P]
    ) -> AsyncCall[P, FormatT]:
        """Decorate an async prompt into an AsyncCall."""
        ...

    @overload
    def __call__(self: CallDecorator[Tool, FormatT], fn: Prompt[P]) -> Call[P, FormatT]:
        """Decorate a prompt into a Call."""
        ...

    def __call__(
        self, fn: Prompt[P] | AsyncPrompt[P]
    ) -> Call[P, FormatT] | AsyncCall[P, FormatT]:
        """Decorates a prompt into a Call."""
        if _prompt_utils.is_async_prompt(fn):
            tools = cast(Sequence[AsyncTool] | None, self.tools)
            return AsyncCall(
                fn=fn,
                default_model=self.model,
                format=self.format,
                toolkit=AsyncToolkit(tools=tools),
            )
        else:
            tools = cast(Sequence[Tool] | None, self.tools)
            return Call(
                fn=fn,
                default_model=self.model,
                format=self.format,
                toolkit=Toolkit(tools=tools),
            )


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


def call(
    *,
    provider: Provider,
    model: Model,
    tools: list[ToolT] | None = None,
    format: type[FormatT] | None = None,
    client: AnthropicClient | GoogleClient | OpenAIClient | None = None,
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
    llm = _utils.assumed_safe_llm_create(
        provider=provider, model=model, client=client, params=params
    )
    return CallDecorator(model=llm, tools=tools, format=format)
