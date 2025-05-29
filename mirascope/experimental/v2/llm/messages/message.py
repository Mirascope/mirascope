"""The `Message` class and its utility constructors."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from ..content import Content


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

    role: Literal["system", "user", "assistant"]
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
    return Message(role="system", content=content, name=name)


def user(content: Content | Sequence[Content], *, name: str | None = None) -> Message:
    """Shorthand method for creating a `Message` with the user role.

    Args:
        content: The content of the message, which can be a string, a Content-type
            object, or a sequence of Content-type objects.
        name: Optional name to identify a specific user in multi-party conversations.

    Returns:
        A Message with the user role.
    """
    return Message(role="user", content=content, name=name)


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
    return Message(role="assistant", content=content, name=name)
