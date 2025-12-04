"""The `prompt` decorator for writing messages as string templates."""

from collections.abc import Sequence
from typing import Generic, cast, overload

from ..context import DepsT
from ..formatting import Format, FormattableT
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
from . import _utils
from .prompts import (
    AsyncContextPrompt,
    AsyncPrompt,
    ContextPrompt,
    Prompt,
)
from .protocols import (
    AsyncContextMessageTemplate,
    AsyncMessageTemplate,
    ContextMessageTemplate,
    MessageTemplate,
)


class PromptDecorator(Generic[ToolT, FormattableT]):
    """Decorator for converting a `MessageTemplate` into a `Prompt`.

    Takes a raw prompt function that returns message content and wraps it with
    tools and format support, creating a `Prompt` that can be called with a model.

    The decorator automatically detects whether the function is async or context-aware
    and creates the appropriate Prompt variant (Prompt, AsyncPrompt, ContextPrompt,
    or AsyncContextPrompt).
    """

    tools: Sequence[ToolT] | None
    """The tools that are included in the prompt, if any."""

    format: type[FormattableT] | Format[FormattableT] | None
    """The structured output format off the prompt, if any."""

    def __init__(
        self,
        tools: Sequence[ToolT] | None = None,
        format: type[FormattableT] | Format[FormattableT] | None = None,
    ) -> None:
        """Initialize the decorator with optional tools and format."""
        self.tools = tools
        self.format = format

    @overload
    def __call__(
        self: "PromptDecorator[AsyncTool | AsyncContextTool[DepsT], FormattableT]",
        fn: AsyncContextMessageTemplate[P, DepsT],
    ) -> AsyncContextPrompt[P, DepsT, FormattableT]:
        """Decorator for creating async context prompts."""
        ...

    @overload
    def __call__(
        self: "PromptDecorator[Tool | ContextTool[DepsT], FormattableT]",
        fn: ContextMessageTemplate[P, DepsT],
    ) -> ContextPrompt[P, DepsT, FormattableT]:
        """Decorator for creating context prompts."""
        ...

    @overload
    def __call__(
        self: "PromptDecorator[AsyncTool, FormattableT]",
        fn: AsyncMessageTemplate[P],
    ) -> AsyncPrompt[P, FormattableT]:
        """Decorator for creating async prompts."""
        ...

    @overload
    def __call__(
        self: "PromptDecorator[Tool, FormattableT]",
        fn: MessageTemplate[P],
    ) -> Prompt[P, FormattableT]:
        """Decorator for creating prompts."""
        ...

    def __call__(
        self,
        fn: ContextMessageTemplate[P, DepsT]
        | AsyncContextMessageTemplate[P, DepsT]
        | MessageTemplate[P]
        | AsyncMessageTemplate[P],
    ) -> (
        Prompt[P, FormattableT]
        | AsyncPrompt[P, FormattableT]
        | ContextPrompt[P, DepsT, FormattableT]
        | AsyncContextPrompt[P, DepsT, FormattableT]
    ):
        """Decorator for creating a prompt with tools and format."""
        is_context = _utils.is_context_promptable(fn)
        is_async = _utils.is_async_promptable(fn)

        if is_context and is_async:
            tools = cast(
                Sequence[AsyncTool | AsyncContextTool[DepsT]] | None, self.tools
            )
            return AsyncContextPrompt(
                fn=fn,
                toolkit=AsyncContextToolkit(tools=tools),
                format=self.format,
            )
        elif is_context:
            tools = cast(Sequence[Tool | ContextTool[DepsT]] | None, self.tools)
            return ContextPrompt(
                fn=fn,
                toolkit=ContextToolkit(tools=tools),
                format=self.format,
            )
        elif is_async:
            tools = cast(Sequence[AsyncTool] | None, self.tools)
            return AsyncPrompt(
                fn=fn, toolkit=AsyncToolkit(tools=tools), format=self.format
            )
        else:
            tools = cast(Sequence[Tool] | None, self.tools)
            return Prompt(fn=fn, toolkit=Toolkit(tools=tools), format=self.format)


@overload
def prompt(  # pyright: ignore[reportOverlappingOverload]
    __fn: ContextMessageTemplate[P, DepsT],
) -> ContextPrompt[P, DepsT, None]:
    """Create a decorator for sync ContextPrompt functions (no arguments)."""
    ...


@overload
def prompt(  # pyright: ignore[reportOverlappingOverload]
    __fn: AsyncContextMessageTemplate[P, DepsT],
) -> AsyncContextPrompt[P, DepsT, None]:
    """Create a decorator for async ContextPrompt functions (no arguments)."""
    ...


@overload
def prompt(
    __fn: MessageTemplate[P],
) -> Prompt[P, None]:
    """Create a decorator for sync Prompt functions (no arguments)."""
    ...


@overload
def prompt(
    __fn: AsyncMessageTemplate[P],
) -> AsyncPrompt[P, None]:
    """Create a decorator for async Prompt functions (no arguments)."""
    ...


@overload
def prompt(
    *,
    tools: Sequence[ToolT] | None = None,
    format: type[FormattableT] | Format[FormattableT] | None = None,
) -> PromptDecorator[ToolT, FormattableT]:
    """Create a decorator for Prompt functions with tools and format"""


def prompt(
    __fn: AsyncContextMessageTemplate[P, DepsT]
    | ContextMessageTemplate[P, DepsT]
    | AsyncMessageTemplate[P]
    | MessageTemplate[P]
    | None = None,
    *,
    tools: Sequence[ToolT] | None = None,
    format: type[FormattableT] | Format[FormattableT] | None = None,
) -> (
    AsyncContextPrompt[P, DepsT, FormattableT]
    | ContextPrompt[P, DepsT, FormattableT]
    | AsyncPrompt[P, FormattableT]
    | Prompt[P, FormattableT]
    | PromptDecorator[ToolT, FormattableT]
):
    """Decorates a `MessageTemplate` to create a `Prompt` callable with a model.

    This decorator transforms a raw prompt function (that returns message content)
    into a `Prompt` object that can be invoked with a model to generate LLM responses.

    The decorator automatically detects the function type:
    - If the first parameter is named `'ctx'` with type `llm.Context[T]`, creates a `ContextPrompt`
    - If the function is async, creates an `AsyncPrompt` or `AsyncContextPrompt`
    - Otherwise, creates a regular `Prompt`

    Args:
        __fn: The prompt function to decorate (optional, for decorator syntax without parens)
        tools: Optional `Sequence` of tools to make available to the LLM
        format: Optional response format class (`BaseModel`) or Format instance

    Returns:
        A `Prompt` variant (Prompt, AsyncPrompt, ContextPrompt, or AsyncContextPrompt)
        or a `PromptDecorator` if called with arguments
    """
    decorator = PromptDecorator(tools=tools, format=format)
    if __fn is None:
        return decorator
    # TODO: See if we can do without the pyright: ignores here
    return decorator(__fn)  # pyright: ignore[reportUnknownVariableType, reportCallIssue]
