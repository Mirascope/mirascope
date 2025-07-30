"""Boundary chunk classes for marking stream start and end points."""

from dataclasses import dataclass
from typing import Literal, TypeAlias

StreamableContentType: TypeAlias = Literal["text", "thinking", "tool_call"]
"""The types of content that can be streamed."""


@dataclass(kw_only=True)
class StartChunk:
    """Marks the beginning of a new content stream.

    This chunk indicates that a new content part (text, thinking, tool_call) is
    about to begin streaming. The content_type field specifies what type of
    content will follow.
    """

    type: Literal["start_chunk"] = "start_chunk"

    content_type: StreamableContentType
    """The type of content that will be streamed after this start marker."""


@dataclass(kw_only=True)
class EndChunk:
    """Marks the end of a content stream.

    This chunk indicates that the current content part has finished streaming.
    No more content chunks of the current type will follow until the next
    StartChunk is encountered.
    """

    type: Literal["end_chunk"] = "end_chunk"

    content_type: StreamableContentType
    """The type of content that just finished streaming."""
