"""The `llm` module for writing provider-agnostic LLM Generations.

This module provides a unified interface for interacting with different LLM providers,
including messages, tools, response formatting, and streaming. It allows you to write
code that works with multiple LLM providers without changing your application logic.
"""

from .messages import (
    Audio,
    Content,
    Document,
    DynamicConfig,
    Image,
    Message,
    PromptTemplate,
    ResponseContent,
    Role,
    Text,
    Thinking,
    ToolCall,
    Video,
    assistant,
    prompt_template,
    system,
    user,
)
from .models import LLM, Client, Params, model
from .response_formatting import (
    ResponseFormat,
    response_format,
)
from .responses import Response
from .streams import AsyncStream, Stream, StreamChunk
from .tools import Tool, ToolDef, ToolOutput, tool

__all__ = [
    "LLM",
    "AsyncStream",
    "Audio",
    "Client",
    "Content",
    "Document",
    "DynamicConfig",
    "Image",
    "Message",
    "Params",
    "PromptTemplate",
    "Response",
    "ResponseContent",
    "ResponseFormat",
    "Role",
    "Stream",
    "StreamChunk",
    "Text",
    "Thinking",
    "Tool",
    "ToolCall",
    "ToolDef",
    "ToolOutput",
    "Video",
    "assistant",
    "model",
    "prompt_template",
    "response_format",
    "system",
    "tool",
    "user",
]
