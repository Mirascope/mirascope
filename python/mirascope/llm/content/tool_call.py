"""The `ToolCall` content class."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal


def normalize_tool_call_args(args: str | None) -> str:
    """Normalize LLM tool-call argument JSON.

    OpenAI Completions/Responses often emit ``arguments=""`` (or whitespace) for
    zero-parameter tools. Treat that as an empty object so downstream
    ``json.loads`` / encode paths match the streaming assembly behavior.
    """
    if args is None or not str(args).strip():
        return "{}"
    return args


def parse_tool_call_args(args: str | None) -> dict[str, object]:
    """Parse tool-call argument JSON, treating empty/whitespace as ``{}``."""
    normalized = normalize_tool_call_args(args)
    parsed = json.loads(normalized)
    if not isinstance(parsed, dict):
        raise TypeError(
            f"Tool call args must be a JSON object, got {type(parsed).__name__}"
        )
    return parsed


@dataclass(kw_only=True)
class ToolCall:
    """Tool call content for a message.

    Represents a request from the assistant to call a tool. This is part of
    an assistant message's content.
    """

    type: Literal["tool_call"] = "tool_call"

    id: str
    """A unique identifier for this tool call."""

    name: str
    """The name of the tool to call."""

    args: str
    """The arguments to pass to the tool, stored as stringified json."""


@dataclass(kw_only=True)
class ToolCallStartChunk:
    """Represents the start of a tool call chunk stream."""

    type: Literal["tool_call_start_chunk"] = "tool_call_start_chunk"

    content_type: Literal["tool_call"] = "tool_call"
    """The type of content reconstructed by this chunk."""

    id: str
    """A unique identifier for this tool call."""

    name: str
    """The name of the tool to call."""


@dataclass(kw_only=True)
class ToolCallChunk:
    """Represents an incremental tool call chunk in a stream."""

    type: Literal["tool_call_chunk"] = "tool_call_chunk"

    content_type: Literal["tool_call"] = "tool_call"
    """The type of content reconstructed by this chunk."""

    id: str
    """A unique identifier for this tool call."""

    delta: str
    """The incremental json args added in this chunk."""


@dataclass(kw_only=True)
class ToolCallEndChunk:
    """Represents the end of a tool call chunk stream."""

    type: Literal["tool_call_end_chunk"] = "tool_call_end_chunk"

    content_type: Literal["tool_call"] = "tool_call"
    """The type of content reconstructed by this chunk."""

    id: str
    """A unique identifier for this tool call."""
