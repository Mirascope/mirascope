"""The `prompt` decorator for writing messages as string templates."""

from collections.abc import Sequence
from typing import overload

from ..context import Context, DepsT
from ..messages import (
    Message,
)
from ..types import P
from . import _utils
from .protocols import (
    AsyncContextPrompt,
    AsyncContextPromptable,
    AsyncPrompt,
    AsyncPromptable,
    ContextPrompt,
    ContextPromptable,
    Prompt,
    Promptable,
)


class PromptDecorator:
    """Protocol for the `prompt` decorator when used without a template."""

    @overload
    def __call__(
        self,
        fn: ContextPromptable[P, DepsT],
    ) -> ContextPrompt[P, DepsT]:
        """Decorator for creating context prompts."""
        ...

    @overload
    def __call__(
        self,
        fn: AsyncContextPromptable[P, DepsT],
    ) -> AsyncContextPrompt[P, DepsT]:
        """Decorator for creating async context prompts."""
        ...

    @overload
    def __call__(
        self,
        fn: Promptable[P],
    ) -> Prompt[P]:
        """Decorator for creating prompts."""
        ...

    @overload
    def __call__(
        self,
        fn: AsyncPromptable[P],
    ) -> AsyncPrompt[P]:
        """Decorator for creating async prompts."""
        ...

    def __call__(
        self,
        fn: ContextPromptable[P, DepsT]
        | AsyncContextPromptable[P, DepsT]
        | Promptable[P]
        | AsyncPromptable[P],
    ) -> (
        Prompt[P]
        | AsyncPrompt[P]
        | ContextPrompt[P, DepsT]
        | AsyncContextPrompt[P, DepsT]
    ):
        """Decorator for creating a prompt."""
        is_context = _utils.is_context_promptable(fn)
        is_async = _utils.is_async_promptable(fn)

        # NOTE: unused `fn` expressions work around a Pyright bug
        # TODO: Clean this up once the following Pyright bug is addressed:
        # https://github.com/microsoft/pyright/issues/10951
        if is_context and is_async:
            fn  # pyright: ignore[reportUnusedExpression]  # noqa: B018

            async def async_context_prompt(
                ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
            ) -> Sequence[Message]:
                result = await fn(ctx, *args, **kwargs)
                return _utils.promote_to_messages(result)

            return async_context_prompt
        elif is_context:
            fn  # pyright: ignore[reportUnusedExpression]  # noqa: B018

            def context_prompt(
                ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
            ) -> Sequence[Message]:
                result = fn(ctx, *args, **kwargs)
                return _utils.promote_to_messages(result)

            return context_prompt
        elif is_async:
            fn  # pyright: ignore[reportUnusedExpression]  # noqa: B018

            async def async_prompt(
                *args: P.args, **kwargs: P.kwargs
            ) -> Sequence[Message]:
                result = await fn(*args, **kwargs)
                return _utils.promote_to_messages(result)

            return async_prompt
        else:
            fn  # pyright: ignore[reportUnusedExpression]  # noqa: B018

            def prompt(*args: P.args, **kwargs: P.kwargs) -> Sequence[Message]:
                result = fn(*args, **kwargs)
                return _utils.promote_to_messages(result)

            return prompt


class PromptTemplateDecorator:
    """Protocol for the `prompt` decorator when used with a template."""

    @overload
    def __call__(
        self,
        fn: ContextPromptable[P, DepsT],
    ) -> ContextPrompt[P, DepsT]:
        """Decorator for creating context prompts from template functions."""
        ...

    @overload
    def __call__(
        self,
        fn: AsyncContextPromptable[P, DepsT],
    ) -> AsyncContextPrompt[P, DepsT]:
        """Decorator for creating async context prompts from template functions."""
        ...

    @overload
    def __call__(
        self,
        fn: Promptable[P],
    ) -> Prompt[P]:
        """Decorator for creating prompts from template functions."""
        ...

    @overload
    def __call__(
        self,
        fn: AsyncPromptable[P],
    ) -> AsyncPrompt[P]:
        """Decorator for creating async prompts from template functions."""
        ...

    def __call__(
        self,
        fn: ContextPromptable[P, DepsT]
        | AsyncContextPromptable[P, DepsT]
        | Promptable[P]
        | AsyncPromptable[P],
    ) -> (
        Prompt[P]
        | AsyncPrompt[P]
        | ContextPrompt[P, DepsT]
        | AsyncContextPrompt[P, DepsT]
    ):
        """Decorator for creating a prompt from a template function."""
        raise NotImplementedError()


@overload
def prompt(
    __fn: ContextPromptable[P, DepsT],
) -> ContextPrompt[P, DepsT]:
    """Create a decorator for sync ContextPrompt functions (no arguments)."""
    ...


@overload
def prompt(
    __fn: AsyncContextPromptable[P, DepsT],
) -> AsyncContextPrompt[P, DepsT]:
    """Create a decorator for async ContextPrompt functions (no arguments)."""
    ...


@overload
def prompt(
    __fn: Promptable[P],
) -> Prompt[P]:
    """Create a decorator for sync Prompt functions (no arguments)."""
    ...


@overload
def prompt(
    __fn: AsyncPromptable[P],
) -> AsyncPrompt[P]:
    """Create a decorator for async Prompt functions (no arguments)."""
    ...


@overload
def prompt(
    *,
    template: None = None,
) -> PromptDecorator:
    """Create a decorator for Prompt functions (no template)"""


@overload
def prompt(
    *,
    template: str,
) -> PromptTemplateDecorator:
    """Create a decorator for template functions."""
    ...


def prompt(
    __fn: ContextPromptable[P, DepsT]
    | AsyncContextPromptable[P, DepsT]
    | Promptable[P]
    | AsyncPromptable[P]
    | None = None,
    *,
    template: str | None = None,
) -> (
    ContextPrompt[P, DepsT]
    | AsyncContextPrompt[P, DepsT]
    | Prompt[P]
    | AsyncPrompt[P]
    | PromptDecorator
    | PromptTemplateDecorator
):
    """Prompt decorator for turning functions (or "Prompts") into prompts.

    This decorator transforms a function into a Prompt, i.e. a function that
    returns `Sequence[llm.Message]`. Its behavior depends on whether it's called with a spec
    string.

    If the first parameter is named 'ctx' or typed as `llm.Context[T]`, it creates
    a ContextPrompt. Otherwise, it creates a regular Prompt.

    With a template string, it returns a PromptTemplateDecorator, in which case it uses
    the provided template to decorate an function with an empty body, and uses arguments
    to the function for variable substitution in the template. The resulting PromptTemplate
    returns messages based on the template.

    Without a template string, it returns a PromptFunctionalDecorator, which
    transforms a Prompt (a function returning either message content, or messages) into
    a PromptTemplate. The resulting prompt template either promotes the content into a
    list containing a single user message, or passes along the messages returned by the
    decorated function.

    Args:
        template: A string template with placeholders using `{{ variable_name }}`
            and optional role markers like [SYSTEM], [USER], and [ASSISTANT].

    Returns:
        A PromptTemplateDecorator or PromptFunctionalDecorator that converts
            the decorated function into a prompt.

    Spec substitution rules:
    - [USER], [ASSISTANT], [SYSTEM] demarcate the start of a new message with that role
    - [MESSAGES] indicates the next variable contains a list of messages to include
    - `{{ variable }}` injects the variable as a string, unless annotated
    - Annotations: `{{ variable:annotation }}` where annotation is one of:
        image, images, audio, audios, document, documents
    - Single content annotations (image, audio, document) expect a file path,
        URL, base64 string, or bytes, which becomes a content part with inferred mime-type
    - Multiple content annotations (images, audios, documents) expect a list
        of strings or bytes, each becoming a content part with inferred mime-type

    Examples:
        ```python
        @llm.prompt
        def answer_question(question: str) -> str:
            return f"Answer this question: {question}"

        @llm.prompt
        def answer_with_context(ctx: llm.Context[str], question: str) -> str:
            return f"Using context {ctx.deps}, answer: {question}"
        ```
    """  # TODO(docs): Update this docstring
    if template:
        raise NotImplementedError()
    decorator = PromptDecorator()
    if __fn is None:
        return decorator
    return decorator(__fn)
