"""The `Message` class and its utility constructors."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from ..content import Content, Text


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
            llm.messages.system("You are a helpful assistant."),
            llm.messages.user("Hello, how are you?"),
        ]
        ```
    """

    role: Literal["system", "user", "assistant"]
    """The role of the message sender (system, user, or assistant)."""

    content: Content | Sequence[Content]
    """The content of the message, which can be text, images, audio, etc."""

    name: str | None = None
    """Optional name to identify specific users or assistants in multi-party conversations."""


def system(
    content: str | Content | Sequence[str | Content], *, name: str | None = None
) -> Message:
    """Shorthand method for creating a `Message` with the system role.

    Args:
        content: The content of the message, which can be a string, a Content-type
            object, or a sequence of Content-type objects.
        name: Optional name to identify a specific system in multi-party conversations.

    Returns:
        A Message with the system role.
    """
    if isinstance(content, str):
        content = Text(text=content)
    return Message(role="system", content=_promote(content), name=name)


def user(
    content: str | Content | Sequence[str | Content], *, name: str | None = None
) -> Message:
    """Shorthand method for creating a `Message` with the user role.

    Args:
        content: The content of the message, which can be a string, a Content-type
            object, or a sequence of Content-type objects.
        name: Optional name to identify a specific user in multi-party conversations.

    Returns:
        A Message with the user role.
    """
    if isinstance(content, str):
        content = Text(text=content)
    return Message(role="user", content=_promote(content), name=name)


def assistant(
    content: str | Content | Sequence[str | Content], *, name: str | None = None
) -> Message:
    """Shorthand method for creating a `Message` with the assistant role.

    Args:
        content: The content of the message, which can be a string, a Content-type
            object, or a sequence of Content-type objects.
        name: Optional name to identify a specific assistant in multi-party conversations.

    Returns:
        A Message with the assistant role.
    """

    return Message(role="assistant", content=_promote(content), name=name)


def _promote(input: str | Content | Sequence[str | Content]) -> Sequence[Content]:
    """Promotes a string or Content object(s) to a sequence of Content objects.

    This ensures consistent handling of message content, converting plain strings
    to Text Content objects where necessary.

    Args:
        input: The input content, which can be a string, a Content object,
               or a sequence of strings and/or Content objects.

    Returns:
        A sequence of Content objects.
    """
    if isinstance(input, str):
        # If it's a single string, wrap it in a list as a Text object
        return [Text(text=input)]
    elif isinstance(input, Content):
        # If it's a single Content object, wrap it in a list
        return [input]
    elif isinstance(input, Sequence):
        # If it's a sequence, iterate and convert strings to Text objects
        promoted_content = []
        for item in input:
            if isinstance(item, str):
                promoted_content.append(Text(text=item))
            elif isinstance(item, Content):
                promoted_content.append(item)
            else:
                # You might want to raise an error or handle other types as needed
                raise TypeError(f"Unsupported content type in sequence: {type(item)}")
        return promoted_content
    else:
        raise TypeError(f"Unsupported input type for promotion: {type(input)}")
