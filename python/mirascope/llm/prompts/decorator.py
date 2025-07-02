"""The `prompt` decorator for writing messages as string templates."""

from collections.abc import Awaitable, Callable, Sequence
from typing import Concatenate, ParamSpec, Protocol, TypeAlias, overload

from typing_extensions import TypeVar

from ..content import Content
from ..context import Context
from ..messages.message import Message

P = ParamSpec("P")
DepsT = TypeVar("DepsT", default=None)


class Prompt(Protocol[P]):
    """Protocol for a prompt function that returns a list of messages."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> list[Message]: ...


class ContentPromptable(Protocol[P]):
    """Protocol for a promptable function that returns a single content part."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Content: ...


class ContentSequencePromptable(Protocol[P]):
    """Protocol for a prompt function that returns a content parts sequence."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Sequence[Content]: ...


Promptable: TypeAlias = ContentPromptable[P] | ContentSequencePromptable[P] | Prompt[P]
"""A function that can be promoted to a prompt.

A `Promptable` function takes input arguments `P` and returns one of:
  - A single `Content` part that will be rendered as a single user message
  - A sequence of `Content` parts that will be rendered as a single user message
  - A list of `Message` objects that will be rendered as-is
"""


class AsyncPrompt(Protocol[P]):
    """Protocol for a prompt function that returns a list of messages."""

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> list[Message]: ...


class AsyncContentPromptable(Protocol[P]):
    """Protocol for a prompt function that returns a single content part."""

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Content: ...


class AsyncContentSequencePromptable(Protocol[P]):
    """Protocol for a prompt function that returns a content parts sequence."""

    async def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Sequence[Content]: ...


AsyncPromptable: TypeAlias = (
    AsyncContentPromptable[P] | AsyncContentSequencePromptable[P] | AsyncPrompt[P]
)
"""An asynchronous promptable function.

An `AsyncPromptable` function takes input arguments `P` and returns one of:
  - A single `Content` part that will be rendered as a single user message
  - A sequence of `Content` parts that will be rendered as a single user message
  - A list of `Message` objects that will be rendered as-is
"""


class ContextPrompt(Protocol[P, DepsT]):
    """Protocol for a context prompt function that returns a list of messages."""

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> list[Message]: ...


class ContextContentPromptable(Protocol[P, DepsT]):
    """Protocol for a context promptable function that returns a single content part."""

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Content: ...


class ContextContentSequencePromptable(Protocol[P, DepsT]):
    """Protocol for a context prompt function that returns a content parts sequence."""

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Sequence[Content]: ...


ContextPromptable: TypeAlias = (
    ContextContentPromptable[P, DepsT]
    | ContextContentSequencePromptable[P, DepsT]
    | ContextPrompt[P, DepsT]
)
"""A context promptable function.

A `ContextPromptable` function takes input arguments `Context[DepsT]` and `P` and
returns one of:
  - A single `Content` part that will be rendered as a single user message
  - A sequence of `Content` parts that will be rendered as a single user message
  - A list of `Message` objects that will be rendered as-is
"""


class AsyncContextPrompt(Protocol[P, DepsT]):
    """Protocol for a context prompt function that returns a list of messages."""

    async def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> list[Message]: ...


class AsyncContextContentPromptable(Protocol[P, DepsT]):
    """Protocol for a context prompt function that returns a single content part."""

    async def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Content: ...


class AsyncContextContentSequencePromptable(Protocol[P, DepsT]):
    """Protocol for a context prompt function that returns a content parts sequence."""

    async def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Sequence[Content]: ...


AsyncContextPromptable: TypeAlias = (
    AsyncContextContentPromptable[P, DepsT]
    | AsyncContextContentSequencePromptable[P, DepsT]
    | AsyncContextPrompt[P, DepsT]
)
"""An asynchronous context promptable function.

An `AsyncContextPromptable` function takes input arguments `Context[DepsT]` and `P` and
returns one of:
  - A single `Content` part that will be rendered as a single user message
  - A sequence of `Content` parts that will be rendered as a single user message
  - A list of `Message` objects that will be rendered as-is
"""


class PromptFunctionalDecorator(Protocol[DepsT]):
    """Protocol for the `prompt` decorator when used without a template."""

    @overload
    def __call__(
        self,
        fn: Callable[Concatenate[Context[DepsT], P], Content]
        | Callable[Concatenate[Context[DepsT], P], Sequence[Content]]
        | Callable[Concatenate[Context[DepsT], P], list[Message]],
    ) -> ContextPrompt[P, DepsT]:
        """Decorator for creating context prompts."""
        ...

    @overload
    def __call__(
        self,
        fn: Callable[Concatenate[Context[DepsT], P], Awaitable[Content]]
        | Callable[Concatenate[Context[DepsT], P], Awaitable[Sequence[Content]]]
        | Callable[Concatenate[Context[DepsT], P], Awaitable[list[Message]]],
    ) -> AsyncContextPrompt[P, DepsT]:
        """Decorator for creating async context prompts."""
        ...

    @overload
    def __call__(
        self,
        fn: Callable[P, Content]
        | Callable[P, Sequence[Content]]
        | Callable[P, list[Message]],
    ) -> Prompt[P]:
        """Decorator for creating prompts."""
        ...

    @overload
    def __call__(
        self,
        fn: Callable[P, Awaitable[Content]]
        | Callable[P, Awaitable[Sequence[Content]]]
        | Callable[P, Awaitable[list[Message]]],
    ) -> AsyncPrompt[P]:
        """Decorator for creating async prompts."""
        ...

    def __call__(
        self,
        fn: Callable[P, Content]
        | Callable[P, Sequence[Content]]
        | Callable[P, list[Message]]
        | Callable[P, Awaitable[Content]]
        | Callable[P, Awaitable[Sequence[Content]]]
        | Callable[P, Awaitable[list[Message]]]
        | Callable[Concatenate[Context[DepsT], P], Content]
        | Callable[Concatenate[Context[DepsT], P], Sequence[Content]]
        | Callable[Concatenate[Context[DepsT], P], list[Message]]
        | Callable[Concatenate[Context[DepsT], P], Awaitable[Content]]
        | Callable[Concatenate[Context[DepsT], P], Awaitable[Sequence[Content]]]
        | Callable[Concatenate[Context[DepsT], P], Awaitable[list[Message]]],
    ) -> (
        Prompt[P]
        | AsyncPrompt[P]
        | ContextPrompt[P, DepsT]
        | AsyncContextPrompt[P, DepsT]
    ):
        """Decorator for creating a prompt."""
        ...


class PromptTemplateDecorator(Protocol[DepsT]):
    """Protocol for the `prompt` decorator when used with a template."""

    @overload
    def __call__(
        self,
        fn: Callable[Concatenate[Context[DepsT], P], None],
    ) -> ContextPrompt[P, DepsT]:
        """Decorator for creating context prompts from template functions."""
        ...

    @overload
    def __call__(
        self,
        fn: Callable[P, None],
    ) -> Prompt[P]:
        """Decorator for creating prompts from template functions."""
        ...

    @overload
    def __call__(
        self,
        fn: Callable[Concatenate[Context[DepsT], P], Awaitable[None]],
    ) -> AsyncContextPrompt[P, DepsT]:
        """Decorator for creating async context prompts from template functions."""
        ...

    @overload
    def __call__(
        self,
        fn: Callable[P, Awaitable[None]],
    ) -> AsyncPrompt[P]:
        """Decorator for creating async prompts from template functions."""
        ...

    def __call__(
        self,
        fn: Callable[P, None]
        | Callable[P, Awaitable[None]]
        | Callable[Concatenate[Context[DepsT], P], None]
        | Callable[Concatenate[Context[DepsT], P], Awaitable[None]],
    ) -> (
        Prompt[P]
        | AsyncPrompt[P]
        | ContextPrompt[P, DepsT]
        | AsyncContextPrompt[P, DepsT]
    ):
        """Decorator for creating a prompt from a template function."""
        ...


@overload
def prompt() -> PromptFunctionalDecorator:
    """Create a decorator for promptable functions (no template)."""
    ...


@overload
def prompt(template: str) -> PromptTemplateDecorator:
    """Create a decorator for template functions."""
    ...


def prompt(
    template: str | None = None,
) -> PromptFunctionalDecorator | PromptTemplateDecorator:
    '''Prompt decorator for turning functions (or "promptables") into prompts.

    This decorator transforms a function into a Prompt, i.e. a function that
    returns `list[llm.Message]`. Its behavior depends on whether it's called with a spec
    string.

    With a spec string, it returns a PromptTemplateDecorator, in which case it uses
    the provided spec to decorate an function with an empty body, and uses arguments
    to the function for variable substitution in the spec. The resulting PromptTemplate
    returns messages based on the spec.

    Without a spec string, it returns a PromptFunctionalDecorator, which
    transforms a Promptable (a function returning either content, content sequence,
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
