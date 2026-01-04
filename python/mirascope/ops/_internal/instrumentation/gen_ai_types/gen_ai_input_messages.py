"""OpenTelemetry Gen AI Semantic Conventions types."""

from __future__ import annotations

from typing import TypeAlias, TypedDict
from typing_extensions import NotRequired

from . import shared


class ChatMessage(TypedDict):
    role: shared.Role | str
    """Role of the entity that created the message."""

    parts: list[
        shared.TextPart
        | shared.ToolCallRequestPart
        | shared.ToolCallResponsePart
        | shared.BlobPart
        | shared.FilePart
        | shared.UriPart
        | shared.ReasoningPart
        | shared.GenericPart
    ]
    """List of message parts that make up the message content."""

    name: NotRequired[str | None]
    """The name of the participant."""


InputMessages: TypeAlias = list[ChatMessage]
