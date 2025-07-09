"""The `Message` class and its utility constructors."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal, TypeAlias

from ..content import AssistantContent, UserContent


@dataclass(kw_only=True)
class SystemMessage:
    """A system message that sets context and instructions for the conversation."""

    role: Literal["system"] = "system"
    content: str


@dataclass(kw_only=True)
class UserMessage:
    """A user message containing input from the user."""

    role: Literal["user"] = "user"
    content: Sequence[UserContent]
    name: str | None = None


@dataclass(kw_only=True)
class AssistantMessage:
    """An assistant message containing the model's response."""

    role: Literal["assistant"] = "assistant"
    content: Sequence[AssistantContent]
    name: str | None = None


Message: TypeAlias = SystemMessage | UserMessage | AssistantMessage
"""A message in an LLM interaction.

Messages have a role (system, user, or assistant) and content that is a sequence
of content parts. The content can include text, images, audio, documents, and
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


def system(content: str) -> SystemMessage:
    """Creates a system message.

    Args:
        content: The content of the message, which must be a string.

    Returns:
        A SystemMessage.
    """
    return SystemMessage(content=content)


def user(
    content: UserContent | Sequence[UserContent], *, name: str | None = None
) -> UserMessage:
    """Creates a user message.

    Args:
        content: The content of the message, which can be `llm.UserContent`, or a sequence of user content pieces.
        name: Optional name to identify a specific user in multi-party conversations.

    Returns:
        A UserMessage.
    """
    if not isinstance(content, Sequence) or isinstance(content, str):
        content = [content]
    return UserMessage(content=content, name=name)


def assistant(
    content: AssistantContent | Sequence[AssistantContent], *, name: str | None = None
) -> AssistantMessage:
    """Creates an assistant message.

    Args:
        content: The content of the message, which can be llm.AssistantContent, or a sequence of assistant content pieces.
        name: Optional name to identify a specific assistant in multi-party conversations.

    Returns:
        An AssistantMessage.
    """
    if not isinstance(content, Sequence) or isinstance(content, str):
        content = [content]
    return AssistantMessage(content=content, name=name)
