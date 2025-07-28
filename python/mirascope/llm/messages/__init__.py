"""The messages module for LLM interactions.

This module defines the message types used in LLM interactions. Messages are represented
as a unified `Message` class with different roles (system, user, assistant) and flexible
content arrays that can include text, images, audio, documents, and tool interactions.
"""

from .message import (
    AssistantMessage,
    AssistantMessagePromotable,
    Message,
    SystemMessage,
    SystemMessagePromotable,
    UserMessage,
    UserMessagePromotable,
    assistant,
    system,
    user,
)

__all__ = [
    "AssistantMessage",
    "AssistantMessagePromotable",
    "Message",
    "SystemMessage",
    "SystemMessagePromotable",
    "UserMessage",
    "UserMessagePromotable",
    "assistant",
    "system",
    "user",
]
