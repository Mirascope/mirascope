"""The `llm.call` decorator for turning `Prompt` functions into LLM calls."""

from __future__ import annotations

import inspect
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic, Literal, cast, get_origin, overload
from typing_extensions import TypeIs, Unpack

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
from ..context import Context, DepsT
from ..formatting import FormatT
from ..models import Model, _utils as _model_utils
from ..prompts import (
    AsyncContextPrompt,
    AsyncPrompt,
    ContextPrompt,
    Prompt,
    _utils as _prompt_utils,
)
from ..tools import (
    AsyncContextTool,
    AsyncContextToolkit,
    AsyncTool,
    AsyncToolkit,
    ContextTool,
    ContextToolkit,
    ContextToolT,
    Tool,
    Toolkit,
)
from ..types import P
from .call import AsyncCall, Call
from .context_call import AsyncContextCall, ContextCall


@dataclass(kw_only=True)
class CallDecorator(Generic[ContextToolT, FormatT]):
    """A decorator for converting prompts to calls."""

    model: Model
    tools: Sequence[ContextToolT] | None
    format: type[FormatT] | None

    @overload
    def __call__(
        self: CallDecorator[AsyncTool | AsyncContextTool[DepsT], FormatT],
        fn: AsyncContextPrompt[P, DepsT],
    ) -> AsyncContextCall[P, DepsT, FormatT]:
        """Decorate an async context prompt into an AsyncContextCall."""
        ...

    @overload
    def __call__(
        self: CallDecorator[Tool | ContextTool[DepsT], FormatT],
        fn: ContextPrompt[P, DepsT],
    ) -> ContextCall[P, DepsT, FormatT]:
        """Decorate a context prompt into a ContextCall."""
        ...

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
        self,
        fn: ContextPrompt[P, DepsT]
        | AsyncContextPrompt[P, DepsT]
        | Prompt[P]
        | AsyncPrompt[P],
    ) -> (
        ContextCall[P, DepsT, FormatT]
        | AsyncContextCall[P, DepsT, FormatT]
        | Call[P, FormatT]
        | AsyncCall[P, FormatT]
    ):
        """Decorates a prompt into a Call or ContextCall."""
        if _is_context_prompt_fn(fn):
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
        elif _prompt_utils.is_async_prompt(fn):
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


def _is_context_prompt_fn(
    fn: ContextPrompt[P, DepsT]
    | AsyncContextPrompt[P, DepsT]
    | Prompt[P]
    | AsyncPrompt[P],
) -> TypeIs[ContextPrompt[P, DepsT] | AsyncContextPrompt[P, DepsT]]:
    """Return whether a prompt function is interpreted as a context prompt.

    If there are no parameters, it isn't a context prompt.
    If the first non-self/cls parameter is typed as Context[T] or subclass of Context, then it is a context prompt.
    """
    sig = inspect.signature(fn)
    params = list(sig.parameters.values())
    if not params:
        return False

    first_param = None
    for param in params:
        if param.name not in ("self", "cls"):
            first_param = param
            break

    if first_param is None or first_param.annotation == inspect.Parameter.empty:
        return False

    origin = get_origin(first_param.annotation)
    if origin is Context:
        return True

    return isinstance(first_param.annotation, type) and issubclass(
        first_param.annotation, Context
    )


@overload
def call(
    *,
    provider: Literal["anthropic"],
    model_id: AnthropicModelId,
    tools: list[ContextToolT] | None = None,
    format: type[FormatT] | None = None,
    **params: Unpack[AnthropicParams],
) -> CallDecorator[ContextToolT, FormatT]:
    """Decorate a prompt into a Call using Anthropic models."""
    ...


@overload
def call(
    *,
    provider: Literal["google"],
    model_id: GoogleModelId,
    tools: list[ContextToolT] | None = None,
    format: type[FormatT] | None = None,
    **params: Unpack[GoogleParams],
) -> CallDecorator[ContextToolT, FormatT]:
    """Decorate a prompt into a Call using Google models."""
    ...


@overload
def call(
    *,
    provider: Literal["openai"],
    model_id: OpenAIModelId,
    tools: list[ContextToolT] | None = None,
    format: type[FormatT] | None = None,
    **params: Unpack[OpenAIParams],
) -> CallDecorator[ContextToolT, FormatT]:
    """Decorate a prompt into a Call using OpenAI models."""
    ...


def call(
    *,
    provider: Provider,
    model_id: ModelId,
    tools: list[ContextToolT] | None = None,
    format: type[FormatT] | None = None,
    **params: Unpack[BaseParams],
) -> CallDecorator[ContextToolT, FormatT]:
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
