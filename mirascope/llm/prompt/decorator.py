"""The `prompt` decorator for writing messages as string templates."""

from collections.abc import Awaitable, Callable, Sequence
from typing import Concatenate, ParamSpec, Protocol, TypeAlias, overload

from typing_extensions import TypeVar

from ..content import Content
from ..context import Context
from ..messages.message import Message

P = ParamSpec("P")
DepsT = TypeVar("DepsT", default=None)


class ContentReturn(Protocol[P]):
    """Protocol for a prompt function that returns a single content part."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Content: ...


class ContextContentReturn(Protocol[P, DepsT]):
    """Protocol for a context prompt function that returns a single content part."""

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Content: ...


class AsyncContentReturn(Protocol[P]):
    """Protocol for a prompt function that returns a single content part."""

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Content: ...


class AsyncContextContentReturn(Protocol[P, DepsT]):
    """Protocol for a context prompt function that returns a single content part."""

    async def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Content: ...


class ContentSequenceReturn(Protocol[P]):
    """Protocol for a prompt function that returns a content parts sequence."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Sequence[Content]: ...


class ContextContentSequenceReturn(Protocol[P, DepsT]):
    """Protocol for a context prompt function that returns a content parts sequence."""

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Sequence[Content]: ...


class AsyncContentSequenceReturn(Protocol[P]):
    """Protocol for a prompt function that returns a content parts sequence."""

    async def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Sequence[Content]: ...


class AsyncContextContentSequenceReturn(Protocol[P, DepsT]):
    """Protocol for a context prompt function that returns a content parts sequence."""

    async def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Sequence[Content]: ...


class MessagesReturn(Protocol[P]):
    """Protocol for a prompt function that returns a list of messages."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> list[Message]: ...


class ContextMessagesReturn(Protocol[P, DepsT]):
    """Protocol for a context prompt function that returns a list of messages."""

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> list[Message]: ...


class AsyncMessagesReturn(Protocol[P]):
    """Protocol for a prompt function that returns a list of messages."""

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> list[Message]: ...


class AsyncContextMessagesReturn(Protocol[P, DepsT]):
    """Protocol for a context prompt function that returns a list of messages."""

    async def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> list[Message]: ...


Prompt: TypeAlias = ContentReturn[P] | ContentSequenceReturn[P] | MessagesReturn[P]
"""A prompt function.

A `Prompt` function takes input arguments `P` and returns one of:
- A single `Content` part that will be rendered as a single user message
- A sequence of `Content` parts that will be rendered as a single user message
- A list of `Message` objects that will be rendered as-is
"""

ContextPrompt: TypeAlias = (
    ContextContentReturn[P, DepsT]
    | ContextContentSequenceReturn[P, DepsT]
    | ContextMessagesReturn[P, DepsT]
)
"""A context prompt function.

A `ContextPrompt` function takes input arguments `Context[DepsT]` and `P` and
returns one of:
- A single `Content` part that will be rendered as a single user message
- A sequence of `Content` parts that will be rendered as a single user message
- A list of `Message` objects that will be rendered as-is
"""

AsyncPrompt: TypeAlias = (
    AsyncContentReturn[P] | AsyncContentSequenceReturn[P] | AsyncMessagesReturn[P]
)
"""An asynchronous prompt function.

An `AsyncPrompt` function takes input arguments `P` and returns one of:
- A single `Content` part that will be rendered as a single user message
- A sequence of `Content` parts that will be rendered as a single user message
- A list of `Message` objects that will be rendered as-is
"""

AsyncContextPrompt: TypeAlias = (
    AsyncContextContentReturn[P, DepsT]
    | AsyncContextContentSequenceReturn[P, DepsT]
    | AsyncContextMessagesReturn[P, DepsT]
)
"""An asynchronous context prompt function.

An `AsyncContextPrompt` function takes input arguments
`Context[DepsT]` and `P` and returns one of:
- A single `Content` part that will be rendered as a single user message
- A sequence of `Content` parts that will be rendered as a single user message
- A list of `Message` objects that will be rendered as-is
"""


class PromptDecorator(Protocol[DepsT]):
    """Protocol for the `prompt` decorator."""

    @overload
    def __call__(self, fn: Callable[Concatenate[Context[DepsT], P], Content]) -> ContextMessagesReturn[P, DepsT]:
        """Decorator for creating a context prompt from a content function."""
        ...

    @overload
    def __call__(self, fn: Callable[Concatenate[Context[DepsT], P], Sequence[Content]]) -> ContextMessagesReturn[P, DepsT]:
        """Decorator for creating a context prompt from a content sequence function."""
        ...

    @overload
    def __call__(self, fn: Callable[Concatenate[Context[DepsT], P], list[Message]]) -> ContextMessagesReturn[P, DepsT]:
        """Decorator for creating a context prompt from a messages function."""
        ...

    @overload
    def __call__(self, fn: Callable[Concatenate[Context[DepsT], P], None]) -> ContextMessagesReturn[P, DepsT]:
        """Decorator for creating a context prompt from a template function."""
        ...

    @overload
    def __call__(self, fn: Callable[Concatenate[Context[DepsT], P], Awaitable[Content]]) -> AsyncContextMessagesReturn[P, DepsT]:
        """Decorator for creating an async context prompt from a content function."""
        ...

    @overload
    def __call__(self, fn: Callable[Concatenate[Context[DepsT], P], Awaitable[Sequence[Content]]]) -> AsyncContextMessagesReturn[P, DepsT]:
        """Decorator for creating an async context prompt from a content sequence function."""
        ...

    @overload
    def __call__(self, fn: Callable[Concatenate[Context[DepsT], P], Awaitable[list[Message]]]) -> AsyncContextMessagesReturn[P, DepsT]:
        """Decorator for creating an async context prompt from a messages function."""
        ...

    @overload
    def __call__(self, fn: Callable[Concatenate[Context[DepsT], P], Awaitable[None]]) -> AsyncContextMessagesReturn[P, DepsT]:
        """Decorator for creating an async context prompt from a template function."""
        ...

    @overload
    def __call__(self, fn: Callable[P, Content]) -> MessagesReturn[P]:
        """Decorator for creating a prompt from a content function."""
        ...

    @overload
    def __call__(self, fn: Callable[P, Sequence[Content]]) -> MessagesReturn[P]:
        """Decorator for creating a prompt from a content sequence function."""
        ...

    @overload
    def __call__(self, fn: Callable[P, list[Message]]) -> MessagesReturn[P]:
        """Decorator for creating a prompt from a messages function."""
        ...

    @overload
    def __call__(self, fn: Callable[P, None]) -> MessagesReturn[P]:
        """Decorator for creating a prompt from a template function."""
        ...

    @overload
    def __call__(self, fn: Callable[P, Awaitable[Content]]) -> AsyncMessagesReturn[P]:
        """Decorator for creating an async prompt from a content function."""
        ...

    @overload
    def __call__(self, fn: Callable[P, Awaitable[Sequence[Content]]]) -> AsyncMessagesReturn[P]:
        """Decorator for creating an async prompt from a content sequence function."""
        ...

    @overload
    def __call__(self, fn: Callable[P, Awaitable[list[Message]]]) -> AsyncMessagesReturn[P]:
        """Decorator for creating an async prompt from a messages function."""
        ...

    @overload
    def __call__(self, fn: Callable[P, Awaitable[None]]) -> AsyncMessagesReturn[P]:
        """Decorator for creating an async prompt from a template function."""
        ...

    def __call__(
        self,
        fn: Callable[P, Content]
        | Callable[P, Sequence[Content]]
        | Callable[P, list[Message]]
        | Callable[P, None]
        | Callable[P, Awaitable[Content]]
        | Callable[P, Awaitable[Sequence[Content]]]
        | Callable[P, Awaitable[list[Message]]]
        | Callable[P, Awaitable[None]]
        | Callable[Concatenate[Context[DepsT], P], Content]
        | Callable[Concatenate[Context[DepsT], P], Sequence[Content]]
        | Callable[Concatenate[Context[DepsT], P], list[Message]]
        | Callable[Concatenate[Context[DepsT], P], None]
        | Callable[Concatenate[Context[DepsT], P], Awaitable[Content]]
        | Callable[Concatenate[Context[DepsT], P], Awaitable[Sequence[Content]]]
        | Callable[Concatenate[Context[DepsT], P], Awaitable[list[Message]]]
        | Callable[Concatenate[Context[DepsT], P], Awaitable[None]],
    ) -> (
        MessagesReturn[P]
        | AsyncMessagesReturn[P]
        | ContextMessagesReturn[P, DepsT]
        | AsyncContextMessagesReturn[P, DepsT]
    ):
        """Decorator for creating a prompt."""
        ...


def prompt(template: str | None = None) -> PromptDecorator:
    '''Prompt decorator for turning functions into prompts.

    This decorator always takes a function and transforms it into a function that
    returns a list of llm.Messages - i.e. a prompt. Its exact behavior depends on
    whether it's called with a template string.

    If called with a template string, then the decorated function should have arguments
    matching variables needing substitution in the template, and an empty
    function body. In this case, the resulting prompt will generate messages as
    specified in the template string.

    If called without a template string, it should decorate a function that returns
    either a single content piece (including strings), or a sequence of content pieces,
    or a list of messages. In this case, the resulting prompt will return either
    a single user message including the supplied content, or (if the function provides
    a list of messages), it will return those messages.

    Args:
        template: A string template with placeholders for variables using the
            format `{{ variable_name }}` and optional section markers like [SYSTEM],
            [USER], and [ASSISTANT].

    Returns:
        A decorator function that converts the decorated function into a prompt.

    Template substitution rules:
    - If [USER], [ASSISTANT], or [SYSTEM] is present, it demarcates the start of a new
    message bearing that role.
    - If [MESSAGES] is present, then the next variable is expected to contain a list of
    messages, which will be included in the resulting messages list.
    - If `{{ variable }}` is present, then that variable will be injected as a string,
    unless an annotation is present.
    - Annotations have the format `{{ variable:annotation }}`, where annotation may be
    one of: image, images, audio, audios, video, videos, document, documents
    - If the image, audio, video, or document annotation is specified, then the variable
    is expected to specify a single piece of content (as a file path, url, base64
    encoded string, or bytes). A corresponding content part will be added to the current
    message, with an automatically inferred mime-type.
    - If the images, audios, videos, or documents annotation is specified, then the
    variable is expected to be a list of strings or bytes that specify individual pieces
    of content, each of which will be added to the current message (with automatically
    inferred mime type).

    Example using a template:
        ```python
        from mirascope import llm

        @llm.prompt("""
            [SYSTEM]
            You are a helpful assistant specializing in {{ domain }}.

            [USER]
            {{ question }}
        """)
        def my_prompt(domain: str, question: str) -> None:
            # This function body should be empty
            pass

        # Use the prompt to generate messages
        messages = my_prompt(domain="astronomy", question="What is a black hole?")
        ```

    Example without a template:
        ```python
        from mirascope import llm
        @llm.prompt()
        def my_prompt(question: str) -> str:
            return f"Answer the question: {question}"
        ```
    '''
    raise NotImplementedError()
