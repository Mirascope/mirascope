"""The `prompt` decorator for writing messages as string templates."""

from collections.abc import Awaitable, Callable
from typing import overload

from ..messages import (
    Message,
)
from ..types import P
from . import _utils
from .types import (
    AsyncMessagesPrompt,
    AsyncPrompt,
    MessagesPrompt,
    Prompt,
)


class PromptDecorator:
    """Protocol for the `prompt` decorator when used without a template."""

    @overload
    def __call__(
        self,
        fn: Prompt[P],
    ) -> MessagesPrompt[P]:
        """Decorator for creating prompts."""
        ...

    @overload
    def __call__(
        self,
        fn: AsyncPrompt[P],
    ) -> AsyncMessagesPrompt[P]:
        """Decorator for creating async prompts."""
        ...

    def __call__(
        self, fn: Prompt[P] | AsyncPrompt[P]
    ) -> MessagesPrompt[P] | AsyncMessagesPrompt[P]:
        """Decorator for creating a prompt."""
        if _utils.is_async_prompt(fn):

            async def async_prompt(*args: P.args, **kwargs: P.kwargs) -> list[Message]:
                result = await fn(*args, **kwargs)
                return _utils.promote_to_messages(result)

            return async_prompt
        else:

            def prompt(*args: P.args, **kwargs: P.kwargs) -> list[Message]:
                result = fn(*args, **kwargs)
                return _utils.promote_to_messages(result)

            return prompt


class PromptTemplateDecorator:
    """Protocol for the `prompt` decorator when used with a template."""

    @overload
    def __call__(
        self,
        fn: Callable[P, None],
    ) -> MessagesPrompt[P]:
        """Decorator for creating prompts from template functions."""
        ...

    @overload
    def __call__(
        self,
        fn: Callable[P, Awaitable[None]],
    ) -> AsyncMessagesPrompt[P]:
        """Decorator for creating async prompts from template functions."""
        ...

    def __call__(
        self, fn: Callable[P, None] | Callable[P, Awaitable[None]]
    ) -> MessagesPrompt[P] | AsyncMessagesPrompt[P]:
        """Decorator for creating a prompt from a template function."""
        raise NotImplementedError()


@overload
def prompt(
    __fn: Prompt[P],
) -> MessagesPrompt[P]:
    """Create a decorator for sync Prompt functions (no arguments)."""
    ...


@overload
def prompt(
    __fn: AsyncPrompt[P],
) -> AsyncMessagesPrompt[P]:
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
    __fn: Prompt[P] | AsyncPrompt[P] | None = None,
    *,
    template: str | None = None,
) -> (
    MessagesPrompt[P]
    | AsyncMessagesPrompt[P]
    | PromptDecorator
    | PromptTemplateDecorator
):
    '''Prompt decorator for turning functions (or "Prompts") into prompts.

    This decorator transforms a function into a Prompt, i.e. a function that
    returns `list[llm.Message]`. Its behavior depends on whether it's called with a spec
    string.

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
        @llm.prompt("""
            [SYSTEM] You are a helpful assistant specializing in {{ domain }}.
            [USER] {{ question }}
        """)
        def domain_question(domain: str, question: str) -> None:
            pass

        @llm.prompt()
        def answer_question(question: str) -> str:
            return f"Answer this question: {question}"
        ```
    '''  # TODO(docs): Update this docstring
    if template:
        raise NotImplementedError()
    decorator = PromptDecorator()
    if __fn is None:
        return decorator
    return decorator(__fn)
