"""The `prompt_template` decorator for writing messages as string templates."""

from collections.abc import Awaitable, Callable, Sequence
from typing import Concatenate, ParamSpec, Protocol, TypeAlias, overload

from typing_extensions import TypeVar

from ..content import Content
from ..context import Context
from ..messages.message import Message
from .dynamic_config import DynamicConfig

P = ParamSpec("P")
DepsT = TypeVar("DepsT", default=None)


class StringReturn(Protocol[P]):
    """Protocol for a prompt template function that returns a single string."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> str: ...


class ContextStringReturn(Protocol[P, DepsT]):
    """Protocol for a context prompt template function that returns a single string."""

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> str: ...


class AsyncStringReturn(Protocol[P]):
    """Protocol for a prompt template function that returns a single string."""

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> str: ...


class AsyncContextStringReturn(Protocol[P, DepsT]):
    """Protocol for a context prompt template function that returns a single string."""

    async def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> str: ...


class ContentReturn(Protocol[P]):
    """Protocol for a prompt template function that returns a single content part."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Content: ...


class ContextContentReturn(Protocol[P, DepsT]):
    """Protocol for a context prompt template function that returns a single content part."""

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Content: ...


class AsyncContentReturn(Protocol[P]):
    """Protocol for a prompt template function that returns a single content part."""

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Content: ...


class AsyncContextContentReturn(Protocol[P, DepsT]):
    """Protocol for a context prompt template function that returns a single content part."""

    async def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Content: ...


class ContentSequenceReturn(Protocol[P]):
    """Protocol for a prompt template function that returns a content parts sequence."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Sequence[Content]: ...


class ContextContentSequenceReturn(Protocol[P, DepsT]):
    """Protocol for a context prompt template function that returns a content parts sequence."""

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Sequence[Content]: ...


class AsyncContentSequenceReturn(Protocol[P]):
    """Protocol for a prompt template function that returns a content parts sequence."""

    async def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Sequence[Content]: ...


class AsyncContextContentSequenceReturn(Protocol[P, DepsT]):
    """Protocol for a context prompt template function that returns a content parts sequence."""

    async def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Sequence[Content]: ...


class MessagesReturn(Protocol[P]):
    """Protocol for a prompt template function that returns a list of messages."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> list[Message]: ...


class ContextMessagesReturn(Protocol[P, DepsT]):
    """Protocol for a context prompt template function that returns a list of messages."""

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> list[Message]: ...


class AsyncMessagesReturn(Protocol[P]):
    """Protocol for a prompt template function that returns a list of messages."""

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> list[Message]: ...


class AsyncContextMessagesReturn(Protocol[P, DepsT]):
    """Protocol for a context prompt template function that returns a list of messages."""

    async def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> list[Message]: ...


class DynamicConfigReturn(Protocol[P]):
    """Protocol for a prompt template function that returns a dynamic configuration."""

    def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> tuple[list[Message], DynamicConfig]: ...


class ContextDynamicConfigReturn(Protocol[P, DepsT]):
    """Protocol for a context prompt template function that returns a dynamic configuration."""

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> tuple[list[Message], DynamicConfig]: ...


class AsyncDynamicConfigReturn(Protocol[P]):
    """Protocol for a prompt template function that returns a dynamic configuration."""

    async def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> tuple[list[Message], DynamicConfig]: ...


class AsyncContextDynamicConfigReturn(Protocol[P, DepsT]):
    """Protocol for a context prompt template function that returns a dynamic configuration."""

    async def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> tuple[list[Message], DynamicConfig]: ...


PromptTemplate: TypeAlias = (
    StringReturn[P]
    | ContentReturn[P]
    | ContentSequenceReturn[P]
    | MessagesReturn[P]
    | DynamicConfigReturn[P]
)
"""A prompt template function.

A `PromptTemplate` function takes input arguments `P` and returns one of:
- A single `str` that will be rendered as a single user message
- A single `Content` part that will be rendered as a single user message
- A sequence of `Content` parts that will be rendered as a single user message
- A list of `Message` objects that will be rendered as-is
- A tuple of a list of `Message` objects that will be rendered as-is and the
      `DynamicConfig` used to render it.
"""

ContextPromptTemplate: TypeAlias = (
    ContextStringReturn[P, DepsT]
    | ContextContentReturn[P, DepsT]
    | ContextContentSequenceReturn[P, DepsT]
    | ContextMessagesReturn[P, DepsT]
    | ContextDynamicConfigReturn[P, DepsT]
)
"""A context prompt template function.

A `ContextPromptTemplate` function takes input arguments `Context[DepsT]` and `P` and
returns one of:
- A single `str` that will be rendered as a single user message
- A single `Content` part that will be rendered as a single user message
- A sequence of `Content` parts that will be rendered as a single user message
- A list of `Message` objects that will be rendered as-is
- A tuple of a list of `Message` objects that will be rendered as-is and the
      `DynamicConfig` used to render it.
"""

AsyncPromptTemplate: TypeAlias = (
    AsyncStringReturn[P]
    | AsyncContentReturn[P]
    | AsyncContentSequenceReturn[P]
    | AsyncMessagesReturn[P]
    | AsyncDynamicConfigReturn[P]
)
"""An asynchronous prompt template function.

An `AsyncPromptTemplate` function takes input arguments `P` and returns one of:
- A single `str` that will be rendered as a single user message
- A single `Content` part that will be rendered as a single user message
- A sequence of `Content` parts that will be rendered as a single user message
- A list of `Message` objects that will be rendered as-is
- A tuple of a list of `Message` objects that will be rendered as-is and the
      `DynamicConfig` used to render it.
"""

AsyncContextPromptTemplate: TypeAlias = (
    AsyncContextStringReturn[P, DepsT]
    | AsyncContextContentReturn[P, DepsT]
    | AsyncContextContentSequenceReturn[P, DepsT]
    | AsyncContextMessagesReturn[P, DepsT]
    | AsyncContextDynamicConfigReturn[P, DepsT]
)
"""An asynchronous context prompt template function.

An `AsyncContextPromptTemplate` function takes input arguments
`Context[DepsT]` and `P` and returns one of:
- A single `str` that will be rendered as a single user message
- A single `Content` part that will be rendered as a single user message
- A sequence of `Content` parts that will be rendered as a single user message
- A list of `Message` objects that will be rendered as-is
- A tuple of a list of `Message` objects that will be rendered as-is and the
      `DynamicConfig` used to render it.
"""


class PromptTemplateDecorator(Protocol[DepsT]):
    """Protocol for the `prompt_template` decorator."""

    @overload
    def __call__(
        self,
        fn: Callable[Concatenate[Context[DepsT], P], None],
    ) -> ContextMessagesReturn[P, DepsT]:
        """Decorator for creating a context prompt template."""
        ...

    @overload
    def __call__(
        self,
        fn: Callable[Concatenate[Context[DepsT], P], DynamicConfig],
    ) -> ContextDynamicConfigReturn[P, DepsT]:
        """Decorator for creating a context dynamic config prompt template."""
        ...

    @overload
    def __call__(
        self,
        fn: Callable[Concatenate[Context[DepsT], P], Awaitable[None]],
    ) -> AsyncContextMessagesReturn[P, DepsT]:
        """Decorator for creating an async context prompt template."""
        ...

    @overload
    def __call__(
        self,
        fn: Callable[Concatenate[Context[DepsT], P], Awaitable[DynamicConfig]],
    ) -> AsyncContextDynamicConfigReturn[P, DepsT]:
        """Decorator for creating an async context dynamic config prompt template."""
        ...

    @overload
    def __call__(self, fn: Callable[P, None]) -> MessagesReturn[P]:
        """Decorator for creating a prompt template."""
        ...

    @overload
    def __call__(self, fn: Callable[P, DynamicConfig]) -> DynamicConfigReturn[P]:
        """Decorator for creating a dynamic config prompt template."""
        ...

    @overload
    def __call__(self, fn: Callable[P, Awaitable[None]]) -> AsyncMessagesReturn[P]:
        """Decorator for creating an async prompt template."""
        ...

    @overload
    def __call__(
        self, fn: Callable[P, Awaitable[DynamicConfig]]
    ) -> AsyncDynamicConfigReturn[P]:
        """Decorator for creating an async dynamic config prompt template."""
        ...

    def __call__(
        self,
        fn: Callable[P, DynamicConfig]
        | Callable[P, None]
        | Callable[P, Awaitable[DynamicConfig]]
        | Callable[P, Awaitable[None]]
        | Callable[Concatenate[Context[DepsT], P], DynamicConfig]
        | Callable[Concatenate[Context[DepsT], P], None]
        | Callable[Concatenate[Context[DepsT], P], Awaitable[DynamicConfig]]
        | Callable[Concatenate[Context[DepsT], P], Awaitable[None]],
    ) -> (
        PromptTemplate[P]
        | AsyncPromptTemplate[P]
        | ContextPromptTemplate[P, DepsT]
        | AsyncContextPromptTemplate[P, DepsT]
    ):
        """Decorator for creating a prompt template."""
        ...


def prompt_template(template: str) -> PromptTemplateDecorator:
    '''Prompt template decorator for writing messages as a string template.

    This decorator transforms a function into a prompt template that will process
    template placeholders and convert sections into messages. Templates can include
    sections like [SYSTEM], [USER], [ASSISTANT] to designate role-specific content.

    Args:
        template: A string template with placeholders for variables using the
            format `{{ variable_name }}` and optional section markers like [SYSTEM],
            [USER], and [ASSISTANT].

    Returns:
        A decorator function that converts the decorated function into a prompt template.

    Example:
        ```python
        from mirascope import llm

        @llm.prompt_template("""
            [SYSTEM]
            You are a helpful assistant specializing in {{ domain }}.

            [USER]
            {{ question }}
        """)
        def my_prompt(domain: str, question: str) -> None:
            # This function body can be empty or contain logic for computing
            # dynamic fields or tools that are returned via DynamicConfig
            pass

        # Use the prompt template to generate messages
        messages = my_prompt(domain="astronomy", question="What is a black hole?")
        ```
    '''
    raise NotImplementedError()
