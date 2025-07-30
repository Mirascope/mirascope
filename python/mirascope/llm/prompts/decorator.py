"""The `prompt` decorator for writing messages as string templates."""

from collections.abc import Awaitable, Callable
from typing import Concatenate, Protocol, overload

from ..context import Context, DepsT
from ..messages import Message, UserMessagePromotable
from ..types import P
from .types import (
    AsyncContextMessagesPrompt,
    AsyncMessagesPrompt,
    ContextMessagesPrompt,
    MessagesPrompt,
)


class PromptDecorator(Protocol[DepsT]):
    """Protocol for the `prompt` decorator when used without a template."""

    @overload
    def __call__(
        self,
        fn: Callable[Concatenate[Context[DepsT], P], UserMessagePromotable]
        | Callable[Concatenate[Context[DepsT], P], list[Message]],
    ) -> ContextMessagesPrompt[P, DepsT]:
        """Decorator for creating context prompts."""
        ...

    @overload
    def __call__(
        self,
        fn: Callable[
            Concatenate[Context[DepsT], P],
            Awaitable[UserMessagePromotable],
        ]
        | Callable[
            Concatenate[Context[DepsT], P],
            Awaitable[list[Message]],
        ],
    ) -> AsyncContextMessagesPrompt[P, DepsT]:
        """Decorator for creating async context prompts."""
        ...

    @overload
    def __call__(
        self,
        fn: Callable[P, UserMessagePromotable] | Callable[P, list[Message]],
    ) -> MessagesPrompt[P]:
        """Decorator for creating prompts."""
        ...

    @overload
    def __call__(
        self,
        fn: Callable[P, Awaitable[UserMessagePromotable]]
        | Callable[P, Awaitable[list[Message]]],
    ) -> AsyncMessagesPrompt[P]:
        """Decorator for creating async prompts."""
        ...

    def __call__(
        self,
        fn: Callable[P, UserMessagePromotable]
        | Callable[P, list[Message]]
        | Callable[P, Awaitable[UserMessagePromotable]]
        | Callable[P, Awaitable[list[Message]]]
        | Callable[
            Concatenate[Context[DepsT], P],
            UserMessagePromotable,
        ]
        | Callable[Concatenate[Context[DepsT], P], list[Message]]
        | Callable[
            Concatenate[Context[DepsT], P],
            Awaitable[UserMessagePromotable],
        ]
        | Callable[
            Concatenate[Context[DepsT], P],
            Awaitable[list[Message]],
        ],
    ) -> (
        MessagesPrompt[P]
        | AsyncMessagesPrompt[P]
        | ContextMessagesPrompt[P, DepsT]
        | AsyncContextMessagesPrompt[P, DepsT]
    ):
        """Decorator for creating a prompt."""
        ...


class PromptTemplateDecorator(Protocol[DepsT]):
    """Protocol for the `prompt` decorator when used with a template."""

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
        fn: Callable[P, None],
    ) -> MessagesPrompt[P]:
        """Decorator for creating prompts from template functions."""
        ...

    @overload
    def __call__(
        self,
        fn: Callable[Concatenate[Context[DepsT], P], Awaitable[None]],
    ) -> AsyncContextMessagesPrompt[P, DepsT]:
        """Decorator for creating async context prompts from template functions."""
        ...

    @overload
    def __call__(
        self,
        fn: Callable[P, Awaitable[None]],
    ) -> AsyncMessagesPrompt[P]:
        """Decorator for creating async prompts from template functions."""
        ...

    def __call__(
        self,
        fn: Callable[P, None]
        | Callable[P, Awaitable[None]]
        | Callable[Concatenate[Context[DepsT], P], None]
        | Callable[Concatenate[Context[DepsT], P], Awaitable[None]],
    ) -> (
        MessagesPrompt[P]
        | AsyncMessagesPrompt[P]
        | ContextMessagesPrompt[P, DepsT]
        | AsyncContextMessagesPrompt[P, DepsT]
    ):
        """Decorator for creating a prompt from a template function."""
        ...


@overload
def prompt() -> PromptDecorator:
    """Create a decorator for Prompt functions (no template)."""
    ...


@overload
def prompt(template: str) -> PromptTemplateDecorator:
    """Create a decorator for template functions."""
    ...


def prompt(
    template: str | None = None,
) -> PromptDecorator | PromptTemplateDecorator:
    '''Prompt decorator for turning functions (or "Prompts") into prompts.

    This decorator transforms a function into a Prompt, i.e. a function that
    returns `list[llm.Message]`. Its behavior depends on whether it's called with a spec
    string.

    With a spec string, it returns a PromptTemplateDecorator, in which case it uses
    the provided spec to decorate an function with an empty body, and uses arguments
    to the function for variable substitution in the spec. The resulting PromptTemplate
    returns messages based on the spec.

    Without a spec string, it returns a PromptFunctionalDecorator, which
    transforms a Prompt (a function returning either message content, or messages) into
    a PromptTemplate. The resulting prompt template either promotes the content into a
    list containing a single user message, or passes along the messages returned by the
    decorated function.

    Args:
        spec: A string spec with placeholders using `{{ variable_name }}`
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
        @llm.prompt_template("""
            [SYSTEM] You are a helpful assistant specializing in {{ domain }}.
            [USER] {{ question }}
        """)
        def domain_question(domain: str, question: str) -> None:
            pass

        @llm.prompt_template()
        def answer_question(question: str) -> str:
            return f"Answer this question: {question}"
        ```
    '''
    raise NotImplementedError()
