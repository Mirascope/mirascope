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
    streams,
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
from .messages import AssistantMessage, Message, SystemMessage, UserMessage
from .models import LLM, model
from .prompts import prompt
from .response_formatting import ResponseFormat
from .response_formatting.decorator import response_format
from .responses import Response
from .streams import (
    AsyncStream,
    AsyncStructuredStream,
    BaseStream,
    Stream,
    StructuredStream,
)
from .tools import Tool, ToolDef
from .tools.decorator import tool

__all__ = [
    "LLM",
    "APIError",
    "Agent",
    "AssistantContent",
    "AssistantMessage",
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
    "BaseStream",
    "Call",
    "ConnectionError",
    "ContentChunk",
    "Context",
    "Document",
    "Image",
    "ImageChunk",
    "ImageUrl",
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
    "SystemMessage",
    "Thinking",
    "ThinkingChunk",
    "TimeoutError",
    "Tool",
    "ToolCall",
    "ToolCallChunk",
    "ToolDef",
    "ToolOutput",
    "UserContent",
    "UserMessage",
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
    "streams",
    "tool",
    "tools",
    "types",
]
