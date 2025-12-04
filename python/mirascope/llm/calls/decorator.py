"""The `llm.call` decorator for turning `Prompt` functions into LLM calls."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic, cast, overload
from typing_extensions import Unpack

from ..clients import ModelId, Params
from ..context import DepsT
from ..formatting import Format, FormattableT
from ..models import Model
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
class CallDecorator(Generic[ToolT, FormattableT]):
    """A decorator for converting prompts to calls."""

    model: Model
    tools: Sequence[ToolT] | None
    format: type[FormattableT] | Format[FormattableT] | None

    @overload
    def __call__(
        self: CallDecorator[AsyncTool | AsyncContextTool[DepsT], FormattableT],
        fn: AsyncContextPromptable[P, DepsT],
    ) -> AsyncContextCall[P, DepsT, FormattableT]:
        """Decorate an async context prompt into an AsyncContextCall."""
        ...

    @overload
    def __call__(
        self: CallDecorator[Tool | ContextTool[DepsT], FormattableT],
        fn: ContextPromptable[P, DepsT],
    ) -> ContextCall[P, DepsT, FormattableT]:
        """Decorate a context prompt into a ContextCall."""
        ...

    @overload
    def __call__(
        self: CallDecorator[AsyncTool, FormattableT], fn: AsyncPromptable[P]
    ) -> AsyncCall[P, FormattableT]:
        """Decorate an async prompt into an AsyncCall."""
        ...

    @overload
    def __call__(
        self: CallDecorator[Tool, FormattableT], fn: Promptable[P]
    ) -> Call[P, FormattableT]:
        """Decorate a prompt into a Call."""
        ...

    def __call__(
        self,
        fn: ContextPromptable[P, DepsT]
        | AsyncContextPromptable[P, DepsT]
        | Promptable[P]
        | AsyncPromptable[P],
    ) -> (
        ContextCall[P, DepsT, FormattableT]
        | AsyncContextCall[P, DepsT, FormattableT]
        | Call[P, FormattableT]
        | AsyncCall[P, FormattableT]
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


def call(
    *,
    model_id: ModelId,
    tools: list[ToolT] | None = None,
    format: type[FormattableT] | Format[FormattableT] | None = None,
    **params: Unpack[Params],
) -> CallDecorator[ToolT, FormattableT]:
    """Returns a decorator for turning prompt template functions into generations.

    This decorator creates a `Call` or `ContextCall` that can be used with prompt functions.
    If the first parameter is typed as `llm.Context[T]`, it creates a ContextCall.
    Otherwise, it creates a regular Call.

    Example:

        Regular call:
        ```python
        from mirascope import llm

        @llm.call(
            model_id="openai/gpt-5-mini",
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
            model_id="openai/gpt-5-mini",
        )
        def answer_question(ctx: llm.Context[Personality], question: str) -> str:
            return f"Your vibe is {ctx.deps.vibe}. Answer this question: {question}"

        ctx = llm.Context(deps=Personality(vibe="snarky"))
        response = answer_question(ctx, "What is the capital of France?")
        print(response)
        ```
    """
    model = Model(model_id=model_id, **params)
    return CallDecorator(model=model, tools=tools, format=format)
