"""Streaming response classes."""

from typing import TypeAlias

from typing_extensions import TypeVar

from .text_stream import AsyncTextStream, TextStream
from .thinking_stream import AsyncThinkingStream, ThinkingStream
from .tool_call_stream import AsyncToolCallStream, ToolCallStream

Stream: TypeAlias = TextStream | ToolCallStream | ThinkingStream
"""An assistant content part that is delivered incrementally."""

AsyncStream: TypeAlias = AsyncTextStream | AsyncToolCallStream | AsyncThinkingStream
"""An assistant content part that is delivered asynchronously and incrementally."""

StreamT = TypeVar("StreamT", bound=Stream | AsyncStream, covariant=True, default=Stream)

__all__ = [
    "AsyncStream",
    "AsyncTextStream",
    "AsyncThinkingStream",
    "AsyncToolCallStream",
    "Stream",
    "StreamT",
    "TextStream",
    "ThinkingStream",
    "ToolCallStream",
]
