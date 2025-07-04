"""The `prompt` decorator for writing messages as string templates."""

from collections.abc import Awaitable, Callable, Sequence
from typing import Concatenate, ParamSpec, Protocol, TypeAlias, overload

from typing_extensions import TypeVar

from ..content import Content
from ..context import Context
from ..messages.message import Message

P = ParamSpec("P")
DepsT = TypeVar("DepsT", default=None)


class MessagesPrompt(Protocol[P]):
    """Protocol for a prompt function that returns a list of messages."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> list[Message]: ...


class ContentPrompt(Protocol[P]):
    """Protocol for a Prompt function that returns a single content part."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Content | str: ...


class ContentSequencePrompt(Protocol[P]):
    """Protocol for a prompt function that returns a content parts sequence."""

    def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Sequence[Content | str]: ...


Prompt: TypeAlias = ContentPrompt[P] | ContentSequencePrompt[P] | MessagesPrompt[P]
"""A function that can be promoted to a prompt.

A `Prompt` function takes input arguments `P` and returns one of:
  - A single `Content | str` part that will be rendered as a single user message
  - A sequence of `Content | str` parts that will be rendered as a single user message
  - A list of `Message` objects that will be rendered as-is
"""


class AsyncMessagesPrompt(Protocol[P]):
    """Protocol for a prompt function that returns a list of messages."""

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> list[Message]: ...


class AsyncContentPrompt(Protocol[P]):
    """Protocol for a prompt function that returns a single content part."""

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Content | str: ...


class AsyncContentSequencePrompt(Protocol[P]):
    """Protocol for a prompt function that returns a content parts sequence."""

    async def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Sequence[Content | str]: ...


AsyncPrompt: TypeAlias = (
    AsyncContentPrompt[P] | AsyncContentSequencePrompt[P] | AsyncMessagesPrompt[P]
)
"""An asynchronous Prompt function.

An `AsyncPrompt` function takes input arguments `P` and returns one of:
  - A single `Content | str` part that will be rendered as a single user message
  - A sequence of `Content | str` parts that will be rendered as a single user message
  - A list of `Message` objects that will be rendered as-is
"""


class ContextMessagesPrompt(Protocol[P, DepsT]):
    """Protocol for a context prompt function that returns a list of messages."""

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> list[Message]: ...


class ContextContentPrompt(Protocol[P, DepsT]):
    """Protocol for a context Prompt function that returns a single content part."""

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Content | str: ...


class ContextContentSequencePrompt(Protocol[P, DepsT]):
    """Protocol for a context prompt function that returns a content parts sequence."""

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Sequence[Content | str]: ...


ContextPrompt: TypeAlias = (
    ContextContentPrompt[P, DepsT]
    | ContextContentSequencePrompt[P, DepsT]
    | ContextMessagesPrompt[P, DepsT]
)
"""A context Prompt function.

A `ContextPrompt` function takes input arguments `Context[DepsT]` and `P` and
returns one of:
  - A single `Content | str` part that will be rendered as a single user message
  - A sequence of `Content | str` parts that will be rendered as a single user message
  - A list of `Message` objects that will be rendered as-is
"""


class AsyncContextMessagesPrompt(Protocol[P, DepsT]):
    """Protocol for a context prompt function that returns a list of messages."""

    async def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> list[Message]: ...


class AsyncContextContentPrompt(Protocol[P, DepsT]):
    """Protocol for a context prompt function that returns a single content part."""

    async def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Content | str: ...


class AsyncContextContentSequencePrompt(Protocol[P, DepsT]):
    """Protocol for a context prompt function that returns a content parts sequence."""

    async def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Sequence[Content | str]: ...


AsyncContextPrompt: TypeAlias = (
    AsyncContextContentPrompt[P, DepsT]
    | AsyncContextContentSequencePrompt[P, DepsT]
    | AsyncContextMessagesPrompt[P, DepsT]
)
"""An asynchronous context Prompt function.

An `AsyncContextPrompt` function takes input arguments `Context[DepsT]` and `P` and
returns one of:
  - A single `Content | str` part that will be rendered as a single user message
  - A sequence of `Content | str` parts that will be rendered as a single user message
  - A list of `Message` objects that will be rendered as-is
"""


class PromptDecorator(Protocol[DepsT]):
    """Protocol for the `prompt` decorator when used without a template."""

    @overload
    def __call__(
        self,
        fn: Callable[Concatenate[Context[DepsT], P], Content | str]
        | Callable[Concatenate[Context[DepsT], P], Sequence[Content | str]]
        | Callable[Concatenate[Context[DepsT], P], list[Message]],
    ) -> ContextMessagesPrompt[P, DepsT]:
        """Decorator for creating context prompts."""
        ...

    @overload
    def __call__(
        self,
        fn: Callable[Concatenate[Context[DepsT], P], Awaitable[Content]]
        | Callable[Concatenate[Context[DepsT], P], Awaitable[Sequence[Content | str]]]
        | Callable[Concatenate[Context[DepsT], P], Awaitable[list[Message]]],
    ) -> AsyncContextMessagesPrompt[P, DepsT]:
        """Decorator for creating async context prompts."""
        ...

    @overload
    def __call__(
        self,
        fn: Callable[P, Content | str]
        | Callable[P, Sequence[Content | str]]
        | Callable[P, list[Message]],
    ) -> MessagesPrompt[P]:
        """Decorator for creating prompts."""
        ...

    @overload
    def __call__(
        self,
        fn: Callable[P, Awaitable[Content]]
        | Callable[P, Awaitable[Sequence[Content | str]]]
        | Callable[P, Awaitable[list[Message]]],
    ) -> AsyncMessagesPrompt[P]:
        """Decorator for creating async prompts."""
        ...

    def __call__(
        self,
        fn: Callable[P, Content | str]
        | Callable[P, Sequence[Content | str]]
        | Callable[P, list[Message]]
        | Callable[P, Awaitable[Content]]
        | Callable[P, Awaitable[Sequence[Content | str]]]
        | Callable[P, Awaitable[list[Message]]]
        | Callable[Concatenate[Context[DepsT], P], Content | str]
        | Callable[Concatenate[Context[DepsT], P], Sequence[Content | str]]
        | Callable[Concatenate[Context[DepsT], P], list[Message]]
        | Callable[Concatenate[Context[DepsT], P], Awaitable[Content]]
        | Callable[Concatenate[Context[DepsT], P], Awaitable[Sequence[Content | str]]]
        | Callable[Concatenate[Context[DepsT], P], Awaitable[list[Message]]],
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
    transforms a Prompt (a function returning either content, content sequence,
    or messages) into a PromptTemplate. The resulting prompt template either promotes
    the content / content sequence into a list containing a single user message with
    that content, or passes along the messages returned by the decorated function.

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
        image, images, audio, audios, video, videos, document, documents
    - Single content annotations (image, audio, video, document) expect a file path,
        URL, base64 string, or bytes, which becomes a content part with inferred mime-type
    - Multiple content annotations (images, audios, videos, documents) expect a list
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
