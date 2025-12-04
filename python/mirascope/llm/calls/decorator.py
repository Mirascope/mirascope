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


@overload
def call(
    model: ModelId,
    *,
    tools: list[ToolT] | None = None,
    format: type[FormattableT] | Format[FormattableT] | None = None,
    **params: Unpack[Params],
) -> CallDecorator[ToolT, FormattableT]:
    """Decorator for converting prompt functions into LLM calls.

    This overload accepts a model ID string and allows additional params.
    """
    ...


@overload
def call(
    model: Model,
    *,
    tools: list[ToolT] | None = None,
    format: type[FormattableT] | Format[FormattableT] | None = None,
) -> CallDecorator[ToolT, FormattableT]:
    """Decorator for converting prompt functions into LLM calls.

    This overload accepts a Model instance and does not allow additional params.
    """
    ...


def call(
    model: ModelId | Model,
    *,
    tools: list[ToolT] | None = None,
    format: type[FormattableT] | Format[FormattableT] | None = None,
    **params: Unpack[Params],
) -> CallDecorator[ToolT, FormattableT]:
    """Decorator for converting prompt functions into LLM calls.

    The `llm.call` decorator is the most convenient way to use Mirascope. It decorates
    a "prompt function" that returns the content provided to the LLM. The decorator
    creates a `Call` or `ContextCall` that can be invoked to call the chosen LLM.

    If the first parameter is typed as `llm.Context[T]`, it creates a `ContextCall`.
    Otherwise, it creates a regular `Call`.

    The model specified in the decorator can be overridden at runtime using the
    `llm.model()` context manager. When overridden, the context model completely
    replaces the decorated model, including all parameters.

    Args:
        model: A model ID string (e.g., "openai/gpt-4") or a `Model` instance
        tools: Optional list of tools to make available to the LLM
        format: Optional response format class (`BaseModel`) or Format instance
        **params: Additional call parameters (temperature, max_tokens, etc.)
            Only available when passing a model ID string

    Returns:
        A `CallDecorator` that converts prompt functions into `Call` or `ContextCall` instances

    Example:

        Regular call:
        ```python
        from mirascope import llm

        @llm.call("openai/gpt-4")
        def recommend_book(genre: str):
            return f"Please recommend a book in {genre}."

        response: llm.Response = recommend_book("fantasy")
        print(response.pretty())
        ```

    Example:

        Context call:
        ```python
        from dataclasses import dataclass
        from mirascope import llm

        @dataclass
        class User:
            name: str
            age: int

        @llm.call("openai/gpt-4")
        def recommend_book(ctx: llm.Context[User], genre: str):
            return f"Recommend a {genre} book for {ctx.deps.name}, age {ctx.deps.age}."

        ctx = llm.Context(deps=User(name="Alice", age=15))
        response = recommend_book(ctx, "fantasy")
        print(response.pretty())
        ```
    """
    if isinstance(model, str):
        model = Model(model, **params)
    return CallDecorator(model=model, tools=tools, format=format)
