"""The `Message` class and its utility constructors."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from ..content import Content, Text


def _promote_content(
    input: str | Content | Sequence[str | Content],
) -> Sequence[Content]:
    """Promotes content (including strings) to a sequence of Content objects.

    Args:
        input: The input content, which can be a string, a Content object,
               or a sequence of strings and/or Content objects.

    Returns:
        A sequence of Content objects.
    """
    if isinstance(input, str):
        return [Text(text=input)]
    elif isinstance(input, Content):
        return [input]
    elif isinstance(input, Sequence):
        promoted_content = []
        for item in input:
            if isinstance(item, str):
                promoted_content.append(Text(text=item))
            else:
                promoted_content.append(item)
        return promoted_content
    else:
        raise TypeError(f"Unsupported input type for promotion: {type(input)}")


@dataclass(kw_only=True)
class Message:
    """A message in an LLM interaction.

    Messages have a role (system, user, or assistant) and content that is a sequence
    of `llm.Content` parts. The content can include text, images, audio, documents, and
    tool interactions.

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

    content: Sequence[Content]
    """The content of the message, which can be text, images, audio, etc."""

    name: str | None = None
    """Optional name to identify specific users or assistants in multi-party conversations."""


def system(
    content: str | Content | Sequence[str | Content], *, name: str | None = None
) -> Message:
    """Shorthand method for creating a `Message` with the system role.

    Args:
        content: The content of the message, which can be a string, a Content-type
            object, or a sequence of strings or Content-type objects.
        name: Optional name to identify a specific system in multi-party conversations.

    Returns:
        A Message with the system role.
    """
    return Message(role="system", content=_promote_content(content), name=name)


def user(
    content: str | Content | Sequence[str | Content], *, name: str | None = None
) -> Message:
    """Shorthand method for creating a `Message` with the user role.

    Args:
        content: The content of the message, which can be a string, a Content-type
            object, or a sequence of strings or Content-type objects.
        name: Optional name to identify a specific user in multi-party conversations.

    Returns:
        A Message with the user role.
    """
    if isinstance(content, str):
        content = Text(text=content)
    return Message(role="user", content=_promote_content(content), name=name)


def assistant(
    content: str | Content | Sequence[str | Content], *, name: str | None = None
) -> Message:
    """Shorthand method for creating a `Message` with the assistant role.

    Args:
        content: The content of the message, which can be a string, a Content-type
            object, or a sequence of strings or Content-type objects.
        name: Optional name to identify a specific assistant in multi-party conversations.

    Returns:
        A Message with the assistant role.
    """

    return Message(role="assistant", content=_promote_content(content), name=name)
