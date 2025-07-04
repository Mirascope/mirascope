"""The `llm` module for writing provider-agnostic LLM Generations.

This module provides a unified interface for interacting with different LLM providers,
including messages, tools, response formatting, and streaming. It allows you to write
code that works with multiple LLM providers without changing your application logic.
"""

from . import (
    agents,
    calls,
    content,
    exceptions,
    messages,
    models,
    prompts,
    response_formatting,
    responses,
    tools,
    types,
)
from .agents import Agent, AsyncAgent, AsyncStructuredAgent, StructuredAgent, agent
from .calls import (
    AsyncCall,
    AsyncStructuredCall,
    Call,
    StructuredCall,
    call,
)
from .clients import BaseClient, BaseParams
from .content import (
    Audio,
    AudioChunk,
    Content,
    ContentChunk,
    Document,
    Image,
    ImageChunk,
    Text,
    TextChunk,
    Thinking,
    ThinkingChunk,
    ToolCall,
    ToolCallChunk,
    ToolOutput,
    Video,
    VideoChunk,
)
from .context import Context, context
from .exceptions import (
    APIError,
    AuthenticationError,
    BadRequestError,
    ConnectionError,
    MirascopeError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    ServerError,
    TimeoutError,
)
from .messages import Message
from .models import LLM, model
from .prompts import prompt
from .response_formatting import ResponseFormat
from .response_formatting.decorator import response_format
from .responses import (
    AsyncStream,
    AsyncStructuredStream,
    Response,
    Stream,
    StructuredStream,
)
from .tools import Tool, ToolDef
from .tools.decorator import tool

__all__ = [
    "LLM",
    "APIError",
    "Agent",
    "AsyncAgent",
    "AsyncCall",
    "AsyncStream",
    "AsyncStructuredAgent",
    "AsyncStructuredCall",
    "AsyncStructuredStream",
    "Audio",
    "AudioChunk",
    "AuthenticationError",
    "BadRequestError",
    "BaseClient",
    "BaseParams",
    "Call",
    "ConnectionError",
    "Content",
    "ContentChunk",
    "Context",
    "Document",
    "Image",
    "ImageChunk",
    "Message",
    "MirascopeError",
    "NotFoundError",
    "PermissionError",
    "RateLimitError",
    "Response",
    "ResponseFormat",
    "ServerError",
    "Stream",
    "StructuredAgent",
    "StructuredCall",
    "StructuredStream",
    "Text",
    "TextChunk",
    "Thinking",
    "ThinkingChunk",
    "TimeoutError",
    "Tool",
    "ToolCall",
    "ToolCallChunk",
    "ToolDef",
    "ToolOutput",
    "Video",
    "VideoChunk",
    "agent",
    "agents",
    "call",
    "calls",
    "content",
    "context",
    "exceptions",
    "messages",
    "model",
    "models",
    "prompts",
    "response_format",
    "response_formatting",
    "responses",
    "tool",
    "tools",
    "types",
]
