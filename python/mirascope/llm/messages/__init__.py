"""The messages module for LLM interactions.

This module defines the message types used in LLM interactions. Messages are represented
as a unified `Message` class with different roles (system, user, assistant) and flexible
content arrays that can include text, images, audio, documents, and tool interactions.
"""

from ._utils import is_messages, promote_to_messages
from .message import (
    AssistantContent,
    AssistantMessage,
    Message,
    SystemContent,
    SystemMessage,
    UserContent,
    UserMessage,
    assistant,
    system,
    user,
)

__all__ = [
    "AssistantContent",
    "AssistantMessage",
    "Message",
    "SystemContent",
    "SystemMessage",
    "UserContent",
    "UserMessage",
    "assistant",
    "is_messages",
    "promote_to_messages",
    "system",
    "user",
]
