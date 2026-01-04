"""OpenTelemetry Gen AI Semantic Conventions types."""

from __future__ import annotations

from typing import Literal, TypeAlias, TypedDict
from typing_extensions import NotRequired

from . import shared

FinishReason: TypeAlias = Literal[
    "stop", "length", "content_filter", "tool_call", "error"
]


class OutputMessage(TypedDict):
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

    finish_reason: FinishReason | str
    """Reason for finishing the generation."""


OutputMessages: TypeAlias = list[OutputMessage]
