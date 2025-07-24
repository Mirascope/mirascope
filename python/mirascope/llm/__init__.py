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
    formatting,
    messages,
    models,
    prompts,
    responses,
    streams,
    tools,
    types,
)
from .agents import Agent, AsyncAgent, agent
from .calls import call, context_call
from .clients import BaseClient, BaseParams
from .content import (
    AssistantContent,
    Audio,
    AudioChunk,
    ContentChunk,
    Document,
    Image,
    ImageChunk,
    ImageUrl,
    Thinking,
    ThinkingChunk,
    ToolCall,
    ToolCallChunk,
    ToolOutput,
    UserContent,
)
from .context import Context
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
    ToolNotFoundError,
)
from .formatting import Format, Partial, format
from .messages import AssistantMessage, Message, SystemMessage, UserMessage
from .models import LLM, model
from .prompts import prompt
from .responses import Response
from .streams import (
    AsyncStream,
    BaseStream,
    Stream,
)
from .tools import Tool, context_tool, tool

__all__ = [
    "LLM",
    "APIError",
    "Agent",
    "AssistantContent",
    "AssistantMessage",
    "AsyncAgent",
    "AsyncStream",
    "AsyncStream",
    "Audio",
    "AudioChunk",
    "AuthenticationError",
    "BadRequestError",
    "BaseClient",
    "BaseParams",
    "BaseStream",
    "ConnectionError",
    "ContentChunk",
    "Context",
    "Document",
    "Format",
    "Image",
    "ImageChunk",
    "ImageUrl",
    "Message",
    "MirascopeError",
    "NotFoundError",
    "Partial",
    "PermissionError",
    "RateLimitError",
    "Response",
    "ServerError",
    "Stream",
    "Stream",
    "SystemMessage",
    "Thinking",
    "ThinkingChunk",
    "TimeoutError",
    "Tool",
    "Tool",
    "ToolCall",
    "ToolCallChunk",
    "ToolNotFoundError",
    "ToolOutput",
    "UserContent",
    "UserMessage",
    "agent",
    "agents",
    "call",
    "calls",
    "content",
    "context_call",
    "context_tool",
    "exceptions",
    "format",
    "formatting",
    "messages",
    "model",
    "models",
    "prompts",
    "responses",
    "streams",
    "tool",
    "tools",
    "types",
]
