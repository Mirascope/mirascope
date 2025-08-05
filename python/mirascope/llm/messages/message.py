"""The `Message` class and its utility constructors."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal, TypeAlias

from ..content import AssistantContentPart, Text, UserContentPart


@dataclass(kw_only=True)
class SystemMessage:
    """A system message that sets context and instructions for the conversation."""

    role: Literal["system"] = "system"
    content: Text


@dataclass(kw_only=True)
class UserMessage:
    """A user message containing input from the user."""

    role: Literal["user"] = "user"
    content: Sequence[UserContentPart]
    name: str | None = None


@dataclass(kw_only=True)
class AssistantMessage:
    """An assistant message containing the model's response."""

    role: Literal["assistant"] = "assistant"
    content: Sequence[AssistantContentPart]
    name: str | None = None


Message: TypeAlias = SystemMessage | UserMessage | AssistantMessage
"""A message in an LLM interaction.

Messages have a role (system, user, or assistant) and content that is a sequence
of content parts. The content can include text, images, audio, documents, and
tool interactions.

For most use cases, prefer the convenience functions `system()`, `user()`, and
`assistant()` instead of directly creating `Message` objects.

Example:

    ```python
    from mirascope import llm

    messages = [
        llm.messages.system("You are a helpful assistant."),
        llm.messages.user("Hello, how are you?"),
    ]
    ```
"""

UserContent: TypeAlias = str | UserContentPart | Sequence[str | UserContentPart]
"""Type alias for content that can fit into a `UserMessage`."""

AssistantContent: TypeAlias = (
    str | AssistantContentPart | Sequence[str | AssistantContentPart]
)
"""Type alias for content that can fit into an `AssistantMessage`."""

SystemContent: TypeAlias = str | Text
"""Type alias for content that can fit into a `SystemMessage`."""


def system(content: SystemContent) -> SystemMessage:
    """Creates a system message.

    Args:
        content: The content of the message, which must be a `str` or `Text` content.

    Returns:
        A `SystemMessage`.
    """
    promoted_content = Text(text=content) if isinstance(content, str) else content
    return SystemMessage(content=promoted_content)


def user(
    content: UserContent,
    *,
    name: str | None = None,
) -> UserMessage:
    """Creates a user message.

    Args:
        content: The content of the message, which can be `str` or any `UserContent`,
            or a sequence of such user content pieces.
        name: Optional name to identify a specific user in multi-party conversations.

    Returns:
        A `UserMessage`.
    """
    if isinstance(content, str) or not isinstance(content, Sequence):
        content = [content]
    promoted_content = [
        Text(text=part) if isinstance(part, str) else part for part in content
    ]
    return UserMessage(content=promoted_content, name=name)


def assistant(
    content: AssistantContent,
    *,
    name: str | None = None,
) -> AssistantMessage:
    """Creates an assistant message.

    Args:
        content: The content of the message, which can be `str` or any `AssistantContent`,
            or a sequence of assistant content pieces.
        name: Optional name to identify a specific assistant in multi-party conversations.

    Returns:
        An `AssistantMessage`.
    """
    if isinstance(content, str) or not isinstance(content, Sequence):
        content = [content]
    promoted_content = [
        Text(text=part) if isinstance(part, str) else part for part in content
    ]
    return AssistantMessage(content=promoted_content, name=name)
