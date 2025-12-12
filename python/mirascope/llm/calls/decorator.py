"""The `llm.call` decorator for turning `Prompt` functions into LLM calls."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic, cast, overload
from typing_extensions import Unpack

from ..context import DepsT
from ..formatting import Format, FormattableT
from ..models import Model
from ..prompts import (
    AsyncContextMessageTemplate,
    AsyncContextPrompt,
    AsyncMessageTemplate,
    AsyncPrompt,
    ContextMessageTemplate,
    ContextPrompt,
    MessageTemplate,
    Prompt,
    _utils,
)
from ..providers import ModelId, Params
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
    """Decorator for converting a `MessageTemplate` into a `Call`.

    Takes a raw prompt function that returns message content and wraps it with tools,
    format, and a model to create a `Call` that can be invoked directly without needing
    to pass a model argument.

    The decorator automatically detects whether the function is async or context-aware
    and creates the appropriate `Call` variant (`Call`, `AsyncCall`, `ContextCall`, or `AsyncContextCall`).

    Conceptually: `CallDecorator` = `PromptDecorator` + `Model`
    Result: `Call` = `MessageTemplate` + tools + format + `Model`
    """

    model: Model
    """The default model to use with this call. May be overridden."""

    tools: Sequence[ToolT] | None
    """The tools that are included in the prompt, if any."""

    format: type[FormattableT] | Format[FormattableT] | None
    """The structured output format off the prompt, if any."""

    @overload
    def __call__(
        self: CallDecorator[AsyncTool | AsyncContextTool[DepsT], FormattableT],
        fn: AsyncContextMessageTemplate[P, DepsT],
    ) -> AsyncContextCall[P, DepsT, FormattableT]:
        """Decorate an async context prompt into an AsyncContextCall."""
        ...

    @overload
    def __call__(
        self: CallDecorator[Tool | ContextTool[DepsT], FormattableT],
        fn: ContextMessageTemplate[P, DepsT],
    ) -> ContextCall[P, DepsT, FormattableT]:
        """Decorate a context prompt into a ContextCall."""
        ...

    @overload
    def __call__(
        self: CallDecorator[AsyncTool, FormattableT], fn: AsyncMessageTemplate[P]
    ) -> AsyncCall[P, FormattableT]:
        """Decorate an async prompt into an AsyncCall."""
        ...

    @overload
    def __call__(
        self: CallDecorator[Tool, FormattableT], fn: MessageTemplate[P]
    ) -> Call[P, FormattableT]:
        """Decorate a prompt into a Call."""
        ...

    def __call__(
        self,
        fn: ContextMessageTemplate[P, DepsT]
        | AsyncContextMessageTemplate[P, DepsT]
        | MessageTemplate[P]
        | AsyncMessageTemplate[P],
    ) -> (
        ContextCall[P, DepsT, FormattableT]
        | AsyncContextCall[P, DepsT, FormattableT]
        | Call[P, FormattableT]
        | AsyncCall[P, FormattableT]
    ):
        """Decorates a prompt into a Call or ContextCall."""
        is_context = _utils.is_context_promptable(fn)
        is_async = _utils.is_async_promptable(fn)

        if is_context and is_async:
            tools = cast(
                Sequence[AsyncTool | AsyncContextTool[DepsT]] | None, self.tools
            )
            prompt = AsyncContextPrompt(
                fn=fn,
                toolkit=AsyncContextToolkit(tools=tools),
                format=self.format,
            )
            return AsyncContextCall(
                prompt=prompt,
                default_model=self.model,
            )
        elif is_context:
            tools = cast(Sequence[Tool | ContextTool[DepsT]] | None, self.tools)
            prompt = ContextPrompt(
                fn=fn,
                toolkit=ContextToolkit(tools=tools),
                format=self.format,
            )
            return ContextCall(
                prompt=prompt,
                default_model=self.model,
            )
        elif is_async:
            tools = cast(Sequence[AsyncTool] | None, self.tools)
            prompt = AsyncPrompt(
                fn=fn, toolkit=AsyncToolkit(tools=tools), format=self.format
            )
            return AsyncCall(
                prompt=prompt,
                default_model=self.model,
            )
        else:
            tools = cast(Sequence[Tool] | None, self.tools)
            prompt = Prompt(fn=fn, toolkit=Toolkit(tools=tools), format=self.format)
            return Call(
                prompt=prompt,
                default_model=self.model,
            )


@overload
def call(
    model: ModelId,
    *,
    tools: Sequence[ToolT] | None = None,
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
    tools: Sequence[ToolT] | None = None,
    format: type[FormattableT] | Format[FormattableT] | None = None,
) -> CallDecorator[ToolT, FormattableT]:
    """Decorator for converting prompt functions into LLM calls.

    This overload accepts a Model instance and does not allow additional params.
    """
    ...


def call(
    model: ModelId | Model,
    *,
    tools: Sequence[ToolT] | None = None,
    format: type[FormattableT] | Format[FormattableT] | None = None,
    **params: Unpack[Params],
) -> CallDecorator[ToolT, FormattableT]:
    """Decorates a `MessageTemplate` to create a `Call` that can be invoked directly.

    The `llm.call` decorator is the most convenient way to use Mirascope. It transforms
    a raw prompt function (that returns message content) into a `Call` object that bundles
    the function with tools, format, and a model. The resulting `Call` can be invoked
    directly to generate LLM responses without needing to pass a model argument.

    The decorator automatically detects the function type:
    - If the first parameter is named `'ctx'` with type `llm.Context[T]` (or a subclass thereof),
      creates a `ContextCall`
    - If the function is async, creates an `AsyncCall` or `AsyncContextCall`
    - Otherwise, creates a regular `Call`

    The model specified in the decorator can be overridden at runtime using the
    `llm.model()` context manager. When overridden, the context model completely
    replaces the decorated model, including all parameters.

    Conceptual flow:
    - `MessageTemplate`: raw function returning content
    - `@llm.prompt`: `MessageTemplate` → `Prompt`
      Includes tools and format, if applicable. Can be called by providing a `Model`.
    - `@llm.call`: `MessageTemplate` → `Call`. Includes a model, tools, and format. The
      model may be created on the fly from a model identifier and optional params, or
      provided outright.

    Args:
        model: A model ID string (e.g., "openai/gpt-4") or a `Model` instance
        tools: Optional `Sequence` of tools to make available to the LLM
        format: Optional response format class (`BaseModel`) or Format instance
        **params: Additional call parameters (temperature, max_tokens, etc.)
            Only available when passing a model ID string

    Returns:
        A `CallDecorator` that converts prompt functions into `Call` variants
        (`Call`, `AsyncCall`, `ContextCall`, or `AsyncContextCall`)

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
