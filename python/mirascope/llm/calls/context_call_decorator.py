"""The `context_call` decorator for turning context prompts into ContextCall instances."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic, Literal, cast, overload
from typing_extensions import Unpack

from ..clients import (
    AnthropicModelId,
    AnthropicParams,
    BaseParams,
    GoogleModelId,
    GoogleParams,
    ModelId,
    OpenAIModelId,
    OpenAIParams,
    Provider,
    get_client,
)
from ..context import DepsT
from ..formatting import FormatT
from ..models import Model, _utils as _model_utils
from ..prompts import (
    AsyncContextPrompt,
    ContextPrompt,
    _utils as _prompt_utils,
)
from ..tools import (
    AsyncContextTool,
    AsyncContextToolkit,
    AsyncTool,
    ContextTool,
    ContextToolkit,
    ContextToolT,
    Tool,
)
from ..types import P
from .context_call import AsyncContextCall, ContextCall


@dataclass(kw_only=True)
class ContextCallDecorator(Generic[ContextToolT, FormatT]):
    """A decorator for converting context prompts to context calls."""

    model: Model
    tools: Sequence[ContextToolT] | None
    format: type[FormatT] | None

    @overload
    def __call__(
        self: ContextCallDecorator[AsyncTool | AsyncContextTool[DepsT], FormatT],
        fn: AsyncContextPrompt[P, DepsT],
    ) -> AsyncContextCall[P, DepsT, FormatT]:
        """Decorate an async context prompt into an AsyncContextCall."""
        ...

    @overload
    def __call__(
        self: ContextCallDecorator[Tool | ContextTool[DepsT], FormatT],
        fn: ContextPrompt[P, DepsT],
    ) -> ContextCall[P, DepsT, FormatT]:
        """Decorate a context prompt into a ContextCall."""
        ...

    def __call__(
        self,
        fn: ContextPrompt[P, DepsT] | AsyncContextPrompt[P, DepsT],
    ) -> ContextCall[P, DepsT, FormatT] | AsyncContextCall[P, DepsT, FormatT]:
        """Decorates a context prompt into a ContextCall."""
        if _prompt_utils.is_async_prompt(fn):
            tools = cast(
                Sequence[AsyncTool | AsyncContextTool[DepsT]] | None, self.tools
            )
            return AsyncContextCall(
                fn=fn,
                default_model=self.model,
                format=self.format,
                toolkit=AsyncContextToolkit(tools=tools),
            )
        else:
            tools = cast(Sequence[Tool | ContextTool[DepsT]] | None, self.tools)
            return ContextCall(
                fn=fn,
                default_model=self.model,
                format=self.format,
                toolkit=ContextToolkit(tools=tools),
            )


@overload
def context_call(
    *,
    provider: Literal["anthropic"],
    model_id: AnthropicModelId,
    tools: list[ContextToolT] | None = None,
    format: type[FormatT] | None = None,
    **params: Unpack[AnthropicParams],
) -> ContextCallDecorator[ContextToolT, FormatT]:
    """Decorate a context prompt into a ContextCall using Anthropic models."""
    ...


@overload
def context_call(
    *,
    provider: Literal["google"],
    model_id: GoogleModelId,
    tools: list[ContextToolT] | None = None,
    format: type[FormatT] | None = None,
    **params: Unpack[GoogleParams],
) -> ContextCallDecorator[ContextToolT, FormatT]:
    """Decorate a context prompt into a ContextCall using Google models."""
    ...


@overload
def context_call(
    *,
    provider: Literal["openai"],
    model_id: OpenAIModelId,
    tools: list[ContextToolT] | None = None,
    format: type[FormatT] | None = None,
    **params: Unpack[OpenAIParams],
) -> ContextCallDecorator[ContextToolT, FormatT]:
    """Decorate a context prompt into a ContextCall using OpenAI models."""
    ...


def context_call(
    *,
    provider: Provider,
    model_id: ModelId,
    tools: list[ContextToolT] | None = None,
    format: type[FormatT] | None = None,
    **params: Unpack[BaseParams],
) -> ContextCallDecorator[ContextToolT, FormatT]:
    """Returns a decorator for turning context prompts into ContextCalls.

    Example:

        ```python
        from dataclasses import dataclass

        from mirascope import llm


        @dataclass
        class Personality:
            vibe: str


        personality = Personality(vibe="snarky")

        @llm.context_call(
            provider="openai",
            model_id="gpt-4o-mini",
        )
        def answer_question(ctx: llm.Context[Personality], question: str) -> str:
            return f"Your vibe is {ctx.deps.vibe}. Answer this question: {question}. "

        ctx: llm.Context = llm.Context(deps=personality)
        response: llm.Response = answer_question(ctx, "What is the capital of France?")
        print(response)
        ```
    """
    llm = _model_utils.assumed_safe_llm_create(
        provider=provider, model_id=model_id, client=get_client(provider), params=params
    )
    return ContextCallDecorator(model=llm, tools=tools, format=format)
