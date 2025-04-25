"""The messages module for LLM interactions.

This module defines the message types used in LLM interactions. Messages are represented
as a unified `Message` class with different roles (system, user, assistant) and flexible
content arrays that can include text, images, audio, documents, and tool interactions.
"""

from ..types.jsonable import Jsonable, JsonableObject
from .message import (
    Message,
    Role,
    assistant,
    system,
    user,
)
from .prompt_template import (
    AsyncContextPromptTemplate,
    AsyncPromptTemplate,
    ContextPromptTemplate,
    DynamicConfig,
    PromptTemplate,
    prompt_template,
)

__all__ = [
    "AsyncContextPromptTemplate",
    "AsyncPromptTemplate",
    "ContextPromptTemplate",
    "DynamicConfig",
    "Jsonable",
    "JsonableObject",
    "Message",
    "PromptTemplate",
    "Role",
    "assistant",
    "prompt_template",
    "system",
    "user",
]
