"""OpenTelemetry Gen AI Semantic Conventions types."""

from __future__ import annotations

from typing import TypeAlias

from . import shared

SystemInstructions: TypeAlias = list[
    shared.TextPart
    | shared.ToolCallRequestPart
    | shared.ToolCallResponsePart
    | shared.BlobPart
    | shared.FilePart
    | shared.UriPart
    | shared.ReasoningPart
    | shared.GenericPart
]
