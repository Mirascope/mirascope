"""Message types for LLM interactions.

This module defines the message types used in LLM interactions. Messages are represented
as a unified `Message` class with different roles (system, user, assistant) and flexible
content arrays that can include text, images, audio, documents, and tool interactions.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Literal, Protocol, TypeAlias, TypeVar, runtime_checkable

JsonableType: TypeAlias = (
    None
    | bool
    | int
    | float
    | str
    | Enum
    | list["JsonableType"]
    | dict[str, "JsonableType"]
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

T = TypeVar("T")
C = TypeVar("C", bound="Content")


@runtime_checkable
class Content(Protocol):
    """Protocol defining the interface for message content parts.

    All content types must implement this protocol. Content objects represent
    the different types of content that can be included in a message, such as
    text, images, audio, documents, or tool interactions.
    """

    @property
    def type(self) -> str:
        """The type of the content part."""
        ...


@dataclass
class Text:
    """Text content for a message.

    This is the most common content type, representing plain text in a message.
    """

    text: str
    """The text content."""

    @property
    def type(self) -> Literal["text"]:
        """The type of the content part."""
        return "text"


@dataclass
class Image:
    """Image content for a message.

    Images can be included in messages to provide visual context. This can be
    used for both input (e.g., user uploading an image) and output (e.g., model
    generating an image).
    """

    image: str | bytes
    """The image data, which can be a URL, file path, base64-encoded string, or binary data."""

    mime_type: Literal["image/png", "image/jpeg", "image/gif", "image/webp"] | str
    """The MIME type of the image, e.g., 'image/png', 'image/jpeg'."""

    @property
    def type(self) -> Literal["image"]:
        """The type of the content part."""
        return "image"


@dataclass
class Audio:
    """Audio content for a message.

    Audio can be included in messages for voice or sound-based interactions.
    """

    audio: str | bytes
    """The audio data, which can be a URL, file path, base64-encoded string, or binary data."""

    mime_type: (
        Literal["audio/mp3", "audio/mpeg", "audio/wav", "audio/ogg", "audio/webm"] | str
    )
    """The MIME type of the audio, e.g., 'audio/mp3', 'audio/wav'."""

    @property
    def type(self) -> Literal["audio"]:
        """The type of the content part."""
        return "audio"


@dataclass
class Document:
    """Document content for a message.

    Documents (like PDFs) can be included for the model to analyze or reference.
    """

    document: str | bytes
    """The document data, which can be a URL, file path, base64-encoded string, or binary data."""

    mime_type: (
        Literal[
            "application/pdf", "text/plain", "text/html", "text/csv", "application/json"
        ]
        | str
    )
    """The MIME type of the document, e.g., 'application/pdf'."""

    @property
    def type(self) -> Literal["document"]:
        """The type of the content part."""
        return "document"


@dataclass
class ToolCall:
    """Tool call content for a message.

    Represents a request from the assistant to call a tool. This is part of
    an assistant message's content.
    """

    name: str
    """The name of the tool to call."""

    args: dict[str, JsonableType]
    """The arguments to pass to the tool."""

    id: str
    """A unique identifier for this tool call."""

    @property
    def type(self) -> Literal["tool_call"]:
        """The type of the content part."""
        return "tool_call"


@dataclass
class ToolOutput:
    """Tool output content for a message.

    Represents the output from a tool call. This is part of a user message's
    content, typically following a tool call from the assistant.
    """

    id: str
    """The ID of the tool call that this output is for."""

    output: JsonableType
    """The output from the tool call."""

    @property
    def type(self) -> Literal["tool_response"]:
        """The type of the content part."""
        return "tool_response"


@dataclass
class Thinking:
    """Thinking content for a message.

    Represents the thinking or thought process of the assistant. This is part
    of an assistant message's content.
    """

    id: str
    """The ID of the thinking content."""

    thoughts: str
    """The thoughts or reasoning of the assistant."""

    redacted: bool = False
    """Whether the thinking is redacted or not."""

    @property
    def type(self) -> Literal["thinking"]:
        """The type of the content part."""
        return "thinking"


class Role(str, Enum):
    """Enumeration of possible message roles."""

    SYSTEM = "system"
    """The system role, used for instructions to the model."""

    USER = "user"
    """The user role, representing the human in the conversation."""

    ASSISTANT = "assistant"
    """The assistant role, representing the AI in the conversation."""


@dataclass
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

    content: str | Content | Sequence[str | Content]
    """The content of the message, which can be text, images, audio, etc."""

    name: str | None = None
    """Optional name to identify specific users or assistants in multi-party conversations."""


def system(
    content: str | Content | Sequence[str | Content], *, name: str | None = None
) -> Message:
    """Shorthand method for creating a `Message` with the system role.

    Args:
        content: The content of the message, which can be a string, a Content object,
            or a sequence of Content objects.
        name: Optional name to identify a specific system in multi-party conversations.

    Returns:
        A Message with the system role.
    """
    return Message(Role.SYSTEM, content, name=name)


def user(
    content: str | Content | Sequence[str | Content], *, name: str | None = None
) -> Message:
    """Shorthand method for creating a `Message` with the user role.

    Args:
        content: The content of the message, which can be a string, a Content object,
            or a sequence of Content objects.
        name: Optional name to identify a specific user in multi-party conversations.

    Returns:
        A Message with the user role.
    """
    return Message(Role.USER, content, name=name)


def assistant(
    content: str | Content | Sequence[str | Content], *, name: str | None = None
) -> Message:
    """Shorthand method for creating a `Message` with the assistant role.

    Args:
        content: The content of the message, which can be a string, a Content object,
            or a sequence of Content objects.
        name: Optional name to identify a specific assistant in multi-party conversations.

    Returns:
        A Message with the assistant role.
    """
    return Message(Role.ASSISTANT, content, name=name)
