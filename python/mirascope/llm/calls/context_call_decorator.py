"""The `llm.call` decorator for turning `Prompt` functions into LLM calls."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, overload

from typing_extensions import Unpack

from ..clients import (
    BaseClient,
    BaseParams,
)
from ..prompts import (
    AsyncContextPrompt,
    ContextPrompt,
)
from ..tools import AsyncContextTool, AsyncTool, ContextTool, ContextToolT, Tool
from ..types import Jsonable
from .context_call import AsyncContextCall, ContextCall

if TYPE_CHECKING:
    from ..clients import (
        REGISTERED_LLMS,
    )


from ..context import DepsT
from ..formatting import FormatT
from ..types import P


class ContextCallDecorator(Protocol[P, ContextToolT, FormatT]):
    """A decorator for converting context prompts to context calls."""

    @overload
    def __call__(
        self: ContextCallDecorator[
            P,
            Tool[..., Jsonable]
            | AsyncTool[..., Jsonable]
            | ContextTool[..., Jsonable, DepsT]
            | AsyncContextTool[..., Jsonable, DepsT],
            FormatT,
        ],
        fn: AsyncContextPrompt[P, DepsT],
    ) -> AsyncContextCall[P, ContextToolT, DepsT, FormatT]:
        """Decorate an async context prompt into an AsyncContextCall."""
        ...

    @overload
    def __call__(
        self: ContextCallDecorator[
            P,
            Tool[..., Jsonable]
            | AsyncTool[..., Jsonable]
            | ContextTool[..., Jsonable, DepsT]
            | AsyncContextTool[..., Jsonable, DepsT],
            FormatT,
        ],
        fn: ContextPrompt[P, DepsT],
    ) -> ContextCall[P, ContextToolT, DepsT, FormatT]:
        """Decorate a context prompt into a ContextCall."""
        ...

    def __call__(
        self: ContextCallDecorator[
            P,
            Tool[..., Jsonable]
            | AsyncTool[..., Jsonable]
            | ContextTool[..., Jsonable, DepsT]
            | AsyncContextTool[..., Jsonable, DepsT],
            FormatT,
        ],
        fn: ContextPrompt[P, DepsT] | AsyncContextPrompt[P, DepsT],
    ) -> (
        ContextCall[P, ContextToolT, DepsT, FormatT]
        | AsyncContextCall[P, ContextToolT, DepsT, FormatT]
    ):
        """Decorates a context prompt into a ContextCall."""
        ...


# @overload
# def context_call(
#     model: ANTHROPIC_REGISTERED_LLMS,
#     *,
#     tools: list[ContextToolT] | None = None,
#     format: type[FormatT] | None = None,
#     client: AnthropicClient | None = None,
#     **params: Unpack[AnthropicParams],
# ) -> ContextCallDecorator[ContextToolT, FormatT]:
#     """Decorate a context prompt into a ContextCall using Anthropic models."""
#     ...


# @overload
# def context_call(
#     model: GOOGLE_REGISTERED_LLMS,
#     *,
#     tools: list[ContextToolT] | None = None,
#     format: type[FormatT] | None = None,
#     client: GoogleClient | None = None,
#     **params: Unpack[GoogleParams],
# ) -> ContextCallDecorator[ContextToolT, FormatT]:
#     """Decorate a context prompt into a ContextCall using Google models."""
#     ...


# @overload
# def context_call(
#     model: OPENAI_REGISTERED_LLMS,
#     *,
#     tools: list[ContextToolT] | None = None,
#     format: type[FormatT] | None = None,
#     client: OpenAIClient | None = None,
#     **params: Unpack[OpenAIParams],
# ) -> ContextCallDecorator[ContextToolT, FormatT]:
#     """Decorate a context prompt into a ContextCall using OpenAI models."""
#     ...


# @overload
# def context_call(
#     model: REGISTERED_LLMS,
#     *,
#     tools: list[ContextToolT] | None = None,
#     format: type[FormatT] | None = None,
#     client: None = None,
#     **params: Unpack[BaseParams],
# ) -> ContextCallDecorator[ContextToolT, FormatT]:
#     """Decorate a context prompt into a ContextCall using any registered model."""
#     ...


def context_call(
    model: REGISTERED_LLMS,
    *,
    tools: list[ContextToolT] | None = None,
    deps_type: type[DepsT] | type[None] | None = None,
    format: type[FormatT] | None = None,
    client: BaseClient | None = None,
    **params: Unpack[BaseParams],
) -> ContextCallDecorator[..., ContextToolT, FormatT]:
    """Returns a decorator for turning context prompts into ContextCalls.

    Example:

        ```python
        from dataclasses import dataclass

        from mirascope import llm


        @dataclass
        class Personality:
            vibe: str


        personality = Personality(vibe="snarky")

        @llm.context_call("openai:gpt-4o-mini")
        def answer_question(ctx: llm.Context[Personality], question: str) -> str:
            return f"Your vibe is {ctx.deps.vibe}. Answer this question: {question}. "

        ctx: llm.Context = llm.Context(deps=personality)
        response: llm.Response = answer_question(ctx, "What is the capital of France?")
        print(response)
        ```
    """
    raise NotImplementedError()
