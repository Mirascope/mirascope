"""The messages module for LLM interactions.

This module defines the message types used in LLM interactions. Messages are represented
as a unified `Message` class with different roles (system, user, assistant) and flexible
content arrays that can include text, images, audio, documents, and tool interactions.
"""

from ..types.jsonable import Jsonable, JsonableObject
from .message import (
    Message,
    assistant,
    system,
    user,
)

__all__ = [
    "Jsonable",
    "JsonableObject",
    "Message",
    "assistant",
    "system",
    "user",
]
