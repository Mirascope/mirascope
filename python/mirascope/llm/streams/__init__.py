"""Streaming response classes."""

from typing import TypeAlias
from typing_extensions import TypeVar

from .text_stream import AsyncTextStream, TextStream
from .thought_stream import AsyncThoughtStream, ThoughtStream
from .tool_call_stream import AsyncToolCallStream, ToolCallStream

Stream: TypeAlias = TextStream | ToolCallStream | ThoughtStream
"""An assistant content part that is delivered incrementally."""

AsyncStream: TypeAlias = AsyncTextStream | AsyncToolCallStream | AsyncThoughtStream
"""An assistant content part that is delivered asynchronously and incrementally."""

StreamT = TypeVar("StreamT", bound=Stream | AsyncStream, covariant=True, default=Stream)

__all__ = [
    "AsyncStream",
    "AsyncTextStream",
    "AsyncThoughtStream",
    "AsyncToolCallStream",
    "Stream",
    "StreamT",
    "TextStream",
    "ThoughtStream",
    "ToolCallStream",
]
