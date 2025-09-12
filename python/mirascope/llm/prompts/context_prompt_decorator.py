"""The `prompt` decorator for writing messages as string templates."""

from collections.abc import Awaitable, Callable
from typing import Concatenate, Generic, Protocol, overload

from ..context import Context, DepsT
from ..messages import (
    Message,
)
from ..types import P
from . import _utils
from .types import (
    AsyncContextMessagesPrompt,
    AsyncContextPrompt,
    ContextMessagesPrompt,
    ContextPrompt,
)


class ContextPromptDecorator(Generic[P, DepsT]):
    """Protocol for the `context_prompt` decorator when used without a template."""

    @overload
    def __call__(
        self,
        fn: ContextPrompt[P, DepsT],
    ) -> ContextMessagesPrompt[P, DepsT]:
        """Decorator for creating context prompts."""
        ...

    @overload
    def __call__(
        self,
        fn: AsyncContextPrompt[P, DepsT],
    ) -> AsyncContextMessagesPrompt[P, DepsT]:
        """Decorator for creating async context prompts."""
        ...

    def __call__(
        self,
        fn: ContextPrompt[P, DepsT] | AsyncContextPrompt[P, DepsT],
    ) -> ContextMessagesPrompt[P, DepsT] | AsyncContextMessagesPrompt[P, DepsT]:
        """Decorator for creating a prompt."""
        if _utils.is_async_prompt(fn):

            async def async_prompt(
                ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
            ) -> list[Message]:
                result = await fn(ctx, *args, **kwargs)
                return _utils.promote_to_messages(result)

            return async_prompt
        else:

            def prompt(
                ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
            ) -> list[Message]:
                result = fn(ctx, *args, **kwargs)
                return _utils.promote_to_messages(result)

            return prompt


class ContextPromptTemplateDecorator(Protocol[DepsT]):
    """Protocol for the `context_prompt` decorator when used with a template."""

    @overload
    def __call__(
        self,
        fn: Callable[Concatenate[Context[DepsT], P], None],
    ) -> ContextMessagesPrompt[P, DepsT]:
        """Decorator for creating context prompts from template functions."""
        ...

    @overload
    def __call__(
        self,
        fn: Callable[Concatenate[Context[DepsT], P], Awaitable[None]],
    ) -> AsyncContextMessagesPrompt[P, DepsT]:
        """Decorator for creating async context prompts from template functions."""
        ...

    def __call__(
        self,
        fn: Callable[Concatenate[Context[DepsT], P], None]
        | Callable[Concatenate[Context[DepsT], P], Awaitable[None]],
    ) -> ContextMessagesPrompt[P, DepsT] | AsyncContextMessagesPrompt[P, DepsT]:
        """Decorator for creating a prompt from a template function."""
        raise NotImplementedError()


@overload
def context_prompt(
    __fn: ContextPrompt[P, DepsT],
) -> ContextMessagesPrompt[P, DepsT]:
    """Create a decorator for sync ContextPrompt functions (no arguments)."""
    ...


@overload
def context_prompt(
    __fn: AsyncContextPrompt[P, DepsT],
) -> AsyncContextMessagesPrompt[P, DepsT]:
    """Create a decorator for async ContextPrompt functions (no arguments)."""
    ...


@overload
def context_prompt(
    *,
    template: None = None,
) -> ContextPromptDecorator:
    """Create a decorator for ContextPrompt functions (no template)"""


@overload
def context_prompt(
    *,
    template: str,
) -> ContextPromptTemplateDecorator:
    """Create a decorator for template functions."""
    ...


def context_prompt(
    __fn: ContextPrompt[P, DepsT] | AsyncContextPrompt[P, DepsT] | None = None,
    *,
    template: str | None = None,
) -> (
    ContextMessagesPrompt[P, DepsT]
    | AsyncContextMessagesPrompt[P, DepsT]
    | ContextPromptDecorator
    | ContextPromptTemplateDecorator
):
    """Returns a Context Prompt (if used as a decorator), or a ContextPromptDecorator."""
    # TODO(docs): Flesh out this docstring
    if template:
        raise NotImplementedError()
    decorator = ContextPromptDecorator()
    if __fn is None:
        return decorator
    return decorator(__fn)
