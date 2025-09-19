"""The `llm.call` decorator for turning `Prompt` functions into LLM calls."""

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
    AsyncContextPromptable,
    AsyncPromptable,
    ContextPromptable,
    Promptable,
    _utils as _prompt_utils,
    prompt,
)
from ..tools import (
    AsyncContextTool,
    AsyncContextToolkit,
    AsyncTool,
    AsyncToolkit,
    ContextTool,
    ContextToolkit,
    Tool,
    Toolkit,
    ToolT,
)
from ..types import P
from .calls import AsyncCall, AsyncContextCall, Call, ContextCall


@dataclass(kw_only=True)
class CallDecorator(Generic[ToolT, FormatT]):
    """A decorator for converting prompts to calls."""

    model: Model
    tools: Sequence[ToolT] | None
    format: type[FormatT] | None

    @overload
    def __call__(
        self: CallDecorator[AsyncTool | AsyncContextTool[DepsT], FormatT],
        fn: AsyncContextPromptable[P, DepsT],
    ) -> AsyncContextCall[P, DepsT, FormatT]:
        """Decorate an async context prompt into an AsyncContextCall."""
        ...

    @overload
    def __call__(
        self: CallDecorator[Tool | ContextTool[DepsT], FormatT],
        fn: ContextPromptable[P, DepsT],
    ) -> ContextCall[P, DepsT, FormatT]:
        """Decorate a context prompt into a ContextCall."""
        ...

    @overload
    def __call__(
        self: CallDecorator[AsyncTool, FormatT], fn: AsyncPromptable[P]
    ) -> AsyncCall[P, FormatT]:
        """Decorate an async prompt into an AsyncCall."""
        ...

    @overload
    def __call__(
        self: CallDecorator[Tool, FormatT], fn: Promptable[P]
    ) -> Call[P, FormatT]:
        """Decorate a prompt into a Call."""
        ...

    def __call__(
        self,
        fn: ContextPromptable[P, DepsT]
        | AsyncContextPromptable[P, DepsT]
        | Promptable[P]
        | AsyncPromptable[P],
    ) -> (
        ContextCall[P, DepsT, FormatT]
        | AsyncContextCall[P, DepsT, FormatT]
        | Call[P, FormatT]
        | AsyncCall[P, FormatT]
    ):
        """Decorates a prompt into a Call or ContextCall."""
        is_context = _prompt_utils.is_context_promptable(fn)
        is_async = _prompt_utils.is_async_promptable(fn)

        if is_context and is_async:
            tools = cast(
                Sequence[AsyncTool | AsyncContextTool[DepsT]] | None, self.tools
            )
            return AsyncContextCall(
                fn=prompt(fn),
                default_model=self.model,
                format=self.format,
                toolkit=AsyncContextToolkit(tools=tools),
            )
        elif is_context:
            tools = cast(Sequence[Tool | ContextTool[DepsT]] | None, self.tools)
            return ContextCall(
                fn=prompt(fn),
                default_model=self.model,
                format=self.format,
                toolkit=ContextToolkit(tools=tools),
            )
        elif is_async:
            tools = cast(Sequence[AsyncTool] | None, self.tools)
            return AsyncCall(
                fn=prompt(fn),
                default_model=self.model,
                format=self.format,
                toolkit=AsyncToolkit(tools=tools),
            )
        else:
            tools = cast(Sequence[Tool] | None, self.tools)
            return Call(
                fn=prompt(fn),
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
    **params: Unpack[BaseParams],
) -> CallDecorator[ToolT, FormatT]:
    """Returns a decorator for turning prompt template functions into generations.

    This decorator creates a `Call` or `ContextCall` that can be used with prompt functions.
    If the first parameter is typed as `llm.Context[T]`, it creates a ContextCall.
    Otherwise, it creates a regular Call.

    Example:

        Regular call:
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

    Example:

        Context call:
        ```python
        from dataclasses import dataclass
        from mirascope import llm

        @dataclass
        class Personality:
            vibe: str

        @llm.call(
            provider="openai",
            model_id="gpt-4o-mini",
        )
        def answer_question(ctx: llm.Context[Personality], question: str) -> str:
            return f"Your vibe is {ctx.deps.vibe}. Answer this question: {question}"

        ctx = llm.Context(deps=Personality(vibe="snarky"))
        response = answer_question(ctx, "What is the capital of France?")
        print(response)
        ```
    """
    llm = _model_utils.assumed_safe_llm_create(
        provider=provider, model_id=model_id, client=get_client(provider), params=params
    )
    return CallDecorator(model=llm, tools=tools, format=format)
