"""Message types for LLM interactions.

This module defines the message types used in LLM interactions. Messages are represented
as a unified `Message` class with different roles (system, user, assistant) and flexible
content arrays that can include text, images, audio, documents, and tool interactions.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Literal, ParamSpec, Protocol, TypeAlias

from typing_extensions import NotRequired, TypedDict

from .tools import Tool, ToolDef, ToolOutput

P = ParamSpec("P")


class Jsonable(Protocol):
    """Protocol for JSON-serializable objects.

    This protocol defines the interface for objects that can be serialized to
    JSON. It is used to annotate the `JsonableType` type alias.
    """

    def json(self) -> str:
        """Serialize the object as a JSON string."""
        ...


JsonableType: TypeAlias = (
    None
    | str
    | int
    | float
    | bool
    | Sequence["JsonableType"]
    | Mapping[str, "JsonableType"]
    | Jsonable
)
"""Simple type alias for JSON-serializable types."""

__all__ = [
    "Audio",
    "Content",
    "Document",
    "Image",
    "Message",
    "Role",
    "Text",
    "Thinking",
    "ToolCall",
    "ToolOutput",
    "assistant",
    "system",
    "user",
]


@dataclass(kw_only=True)
class Text:
    """Text content for a message.

    This is the most common content type, representing plain text in a message.
    """

    type: Literal["text"] = "text"

    text: str
    """The text content."""


@dataclass(kw_only=True)
class Image:
    """Image content for a message.

    Images can be included in messages to provide visual context. This can be
    used for both input (e.g., user uploading an image) and output (e.g., model
    generating an image).
    """

    type: Literal["image"] = "image"

    data: str | bytes
    """The image data, which can be a URL, file path, base64-encoded string, or binary data."""

    mime_type: Literal[
        "image/png",
        "image/jpeg",
        "image/webp",
        "image/gif",
        "image/heic",
        "image/heif",
    ]
    """The MIME type of the image, e.g., 'image/png', 'image/jpeg'."""


@dataclass(kw_only=True)
class Audio:
    """Audio content for a message.

    Audio can be included in messages for voice or sound-based interactions.
    """

    type: Literal["audio"] = "audio"

    data: str | bytes
    """The audio data, which can be a URL, file path, base64-encoded string, or binary data."""

    mime_type: Literal[
        "audio/wav",
        "audio/mp3",
        "audio/aiff",
        "audio/aac",
        "audio/ogg",
        "audio/flac",
    ]
    """The MIME type of the audio, e.g., 'audio/mp3', 'audio/wav'."""


@dataclass(kw_only=True)
class Video:
    """Video content for a message.

    Video can be included in messages for video-based interactions.
    """

    type: Literal["video"] = "video"

    data: str | bytes
    """The video data, which can be a URL, file path, base64-encoded string, or binary data."""

    mime_type: Literal[
        "video/mp4",
        "video/mpeg",
        "video/mov",
        "video/avi",
        "video/x-flv",
        "video/mpg",
        "video/webm",
        "video/wmv",
        "video/3gpp",
    ]
    """The MIME type of the video, e.g., 'video/mp4', 'video/webm'."""


@dataclass(kw_only=True)
class Document:
    """Document content for a message.

    Documents (like PDFs) can be included for the model to analyze or reference.
    """

    type: Literal["document"] = "document"

    data: str | bytes
    """The document data, which can be a URL, file path, base64-encoded string, or binary data."""

    mime_type: Literal[
        "application/pdf",
        "application/json",
        "text/plain",
        "application/x-javascript",
        "text/javascript",
        "application/x-python",
        "text/x-python",
        "text/html",
        "text/css",
        "text/xml",
        "text/rtf",
    ]
    """The MIME type of the document, e.g., 'application/pdf'."""


@dataclass(kw_only=True)
class ToolCall:
    """Tool call content for a message.

    Represents a request from the assistant to call a tool. This is part of
    an assistant message's content.
    """

    type: Literal["tool_call"] = "tool_call"

    name: str
    """The name of the tool to call."""

    args: dict[str, JsonableType]
    """The arguments to pass to the tool."""

    id: str
    """A unique identifier for this tool call."""


@dataclass(kw_only=True)
class Thinking:
    """Thinking content for a message.

    Represents the thinking or thought process of the assistant. This is part
    of an assistant message's content.
    """

    type: Literal["thinking"] = "thinking"

    id: str
    """The ID of the thinking content."""

    thoughts: str
    """The thoughts or reasoning of the assistant."""

    redacted: bool = False
    """Whether the thinking is redacted or not."""


Content: TypeAlias = (
    str | Text | Image | Audio | Video | Document | ToolCall | ToolOutput | Thinking
)
ResponseContent: TypeAlias = str | Image | Audio | Video | Tool


class Role(str, Enum):
    """Enumeration of possible message roles."""

    SYSTEM = "system"
    """The system role, used for instructions to the model."""

    USER = "user"
    """The user role, representing the human in the conversation."""

    ASSISTANT = "assistant"
    """The assistant role, representing the AI in the conversation."""


@dataclass(kw_only=True)
class Message:
    """A message in an LLM interaction.

    Messages have a role (system, user, or assistant) and content that can be
    a simple string or a complex array of content parts. The content can include
    text, images, audio, documents, and tool interactions.

    For most use cases, prefer the convenience functions system(), user(), and
    assistant() instead of directly creating Message objects.

    Example:

        ```python
        from mirascope import llm

        messages = [
            llm.system("You are a helpful assistant."),
            llm.user("Hello, how are you?"),
        ]
        ```
    """

    role: Role
    """The role of the message sender (system, user, or assistant)."""

    content: Content | Sequence[Content]
    """The content of the message, which can be text, images, audio, etc."""

    name: str | None = None
    """Optional name to identify specific users or assistants in multi-party conversations."""


def system(content: Content | Sequence[Content], *, name: str | None = None) -> Message:
    """Shorthand method for creating a `Message` with the system role.

    Args:
        content: The content of the message, which can be a string, a Content-type
            object, or a sequence of Content-type objects.
        name: Optional name to identify a specific system in multi-party conversations.

    Returns:
        A Message with the system role.
    """
    return Message(role=Role.SYSTEM, content=content, name=name)


def user(content: Content | Sequence[Content], *, name: str | None = None) -> Message:
    """Shorthand method for creating a `Message` with the user role.

    Args:
        content: The content of the message, which can be a string, a Content-type
            object, or a sequence of Content-type objects.
        name: Optional name to identify a specific user in multi-party conversations.

    Returns:
        A Message with the user role.
    """
    return Message(role=Role.USER, content=content, name=name)


def assistant(
    content: Content | Sequence[Content], *, name: str | None = None
) -> Message:
    """Shorthand method for creating a `Message` with the assistant role.

    Args:
        content: The content of the message, which can be a string, a Content-type
            object, or a sequence of Content-type objects.
        name: Optional name to identify a specific assistant in multi-party conversations.

    Returns:
        A Message with the assistant role.
    """
    return Message(role=Role.ASSISTANT, content=content, name=name)


class DynamicConfig(TypedDict):
    """Class for specifying dynamic configuration in a prompt template method.

    This class allows prompt template functions to return additional configuration
    options that will be applied during message generation, such as computed fields
    that should be injected into the template or tools that should be made available
    to the LLM.
    """

    computed_fields: NotRequired[dict[str, JsonableType]]
    """The fields injected into the messages that are computed dynamically.
    
    These fields will be available for use in the template with the {{ field_name }} syntax,
    and will override any fields with the same name provided in the function arguments.
    """

    tools: NotRequired[Sequence[ToolDef]]
    """The list of dynamic tools to merge into the existing tools in the LLM call.
    
    These tools will be added to any tools specified in the generation decorator
    or at generation call time.
    """


class PromptTemplate(Protocol[P]):
    """Protocol for a prompt template function.

    This protocol defines the interface for a prompt template, which is used to create
    a list of messages based on a given input. The template can be used to generate
    messages for different roles (system, user, assistant) by parsing a string template
    with sections and variable placeholders.

    Functions decorated with `@prompt_template` will implement this protocol.
    """

    def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> list[Message] | tuple[list[Message], DynamicConfig]:
        """Renders the list of messages (and dynamic config) given input arguments.

        Args:
            *args: Positional arguments to pass to the template function.
            **kwargs: Keyword arguments to pass to the template function.

        Returns:
            Either a list of messages, or a tuple containing a list of messages and
            a DynamicConfig object with additional configuration options.
        """
        ...


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
