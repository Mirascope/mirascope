"""The `prompt_template` decorator for writing messages as string templates."""

from collections.abc import Callable, Sequence
from typing import ParamSpec, Protocol, TypeAlias

from typing_extensions import NotRequired, TypedDict

from ..content import Content
from ..tools import ToolDef
from ..types import Jsonable
from .message import Message

P = ParamSpec("P")


class DynamicConfig(TypedDict):
    """Class for specifying dynamic configuration in a prompt template method.

    This class allows prompt template functions to return additional configuration
    options that will be applied during message rendering, such as computed fields
    that should be injected into the template or tools that should be made available
    to the LLM.
    """

    computed_fields: NotRequired[dict[str, Jsonable]]
    """The fields injected into the messages that are computed dynamically.
    
    These fields will be available for use in the template with the {{ field_name }} syntax,
    and will override any fields with the same name provided in the function arguments.
    """

    tools: NotRequired[Sequence[ToolDef]]
    """The list of dynamic tools to merge into the existing tools in the LLM call.
    
    These tools will be added to any tools specified in the call decorator.
    """


class StringReturn(Protocol[P]):
    """Protocol for a prompt template function that returns a single string."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> str: ...


class AsyncStringReturn(Protocol[P]):
    """Protocol for a prompt template function that returns a single string."""

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> str: ...


class ContentReturn(Protocol[P]):
    """Protocol for a prompt template function that returns a single content part."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Content: ...


class AsyncContentReturn(Protocol[P]):
    """Protocol for a prompt template function that returns a single content part."""

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Content: ...


class ContentSequenceReturn(Protocol[P]):
    """Protocol for a prompt template function that returns a content parts sequence."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Sequence[Content]: ...


class AsyncContentSequenceReturn(Protocol[P]):
    """Protocol for a prompt template function that returns a content parts sequence."""

    async def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Sequence[Content]: ...


class MessagesReturn(Protocol[P]):
    """Protocol for a prompt template function that returns a list of messages."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> list[Message]: ...


class AsyncMessagesReturn(Protocol[P]):
    """Protocol for a prompt template function that returns a list of messages."""

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> list[Message]: ...


class DynamicConfigReturn(Protocol[P]):
    """Protocol for a prompt template function that returns a dynamic configuration."""

    def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> tuple[list[Message], DynamicConfig]: ...


class AsyncDynamicConfigReturn(Protocol[P]):
    """Protocol for a prompt template function that returns a dynamic configuration."""

    async def __call__(
        self, *args: P.args, **kwargs: P.kwargs
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


def prompt_template(
    template: str,
) -> Callable[[Callable[P, None | DynamicConfig]], PromptTemplate[P]]:
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
