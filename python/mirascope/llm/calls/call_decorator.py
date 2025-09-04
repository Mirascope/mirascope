"""The `llm.call` decorator for turning `Prompt` functions into LLM calls."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, Literal, cast, overload
from typing_extensions import Unpack

from ..models import LLM, _utils as _model_utils
from ..prompts import AsyncPrompt, Prompt, _utils as _prompt_utils
from ..tools import AsyncTool, Tool, ToolT
from .call import AsyncCall, Call

if TYPE_CHECKING:
    from ..clients import (
        AnthropicClient,
        AnthropicModelId,
        AnthropicParams,
        BaseParams,
        GoogleClient,
        GoogleModelId,
        GoogleParams,
        ModelId,
        OpenAIClient,
        OpenAIModelId,
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
    model_id: AnthropicModelId,
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
    model_id: GoogleModelId,
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
    model_id: OpenAIModelId,
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
    model_id: ModelId,
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
            model_id="gpt-4o-mini",
        )
        def answer_question(question: str) -> str:
            return f"Answer this question: {question}"

        response: llm.Response = answer_question("What is the capital of France?")
        print(response)
        ```
    """
    llm = _model_utils.assumed_safe_llm_create(
        provider=provider, model_id=model_id, client=client, params=params
    )
    return CallDecorator(model=llm, tools=tools, format=format)
