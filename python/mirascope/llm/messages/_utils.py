"""Utility functions for message handling."""

from collections.abc import Sequence
from typing_extensions import TypeIs

from .message import (
    AssistantMessage,
    Message,
    SystemMessage,
    UserContent,
    UserMessage,
    user,
)


def is_messages(
    content: UserContent | Sequence[Message],
) -> TypeIs[Sequence[Message]]:
    if isinstance(content, list):
        if not content:
            raise ValueError("Empty array may not be used as message content")
        return isinstance(content[0], SystemMessage | UserMessage | AssistantMessage)
    return False


def promote_to_messages(content: UserContent | Sequence[Message]) -> Sequence[Message]:
    """Promote a prompt result to a list of messages.

    If the result is already a list of Messages, returns it as-is.
    If the result is str/UserContentPart/Sequence of content parts, wraps it in a user message.
    """
    if is_messages(content):
        return content
    return [user(content)]
