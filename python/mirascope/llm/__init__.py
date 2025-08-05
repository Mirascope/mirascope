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
    mcp,
    messages,
    models,
    prompts,
    responses,
    streams,
    tools,
    types,
)
from .agents import Agent, AgentTemplate, AsyncAgent, AsyncAgentTemplate, agent
from .calls import call, context_call
from .clients import BaseClient, BaseParams
from .content import (
    AssistantContentPart,
    Audio,
    Document,
    Image,
    ImageUrl,
    Text,
    Thinking,
    ToolCall,
    ToolOutput,
    UserContentPart,
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
from .responses import FinishReason, Response, StreamResponse
from .streams import AsyncStream, Stream
from .tools import Tool, context_tool, tool

__all__ = [
    "LLM",
    "APIError",
    "Agent",
    "AgentTemplate",
    "AssistantContentPart",
    "AssistantMessage",
    "AsyncAgent",
    "AsyncAgentTemplate",
    "AsyncStream",
    "Audio",
    "AuthenticationError",
    "BadRequestError",
    "BaseClient",
    "BaseParams",
    "ConnectionError",
    "Context",
    "Document",
    "FinishReason",
    "Format",
    "Image",
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
    "StreamResponse",
    "StreamResponse",
    "SystemMessage",
    "Text",
    "Thinking",
    "TimeoutError",
    "Tool",
    "Tool",
    "ToolCall",
    "ToolNotFoundError",
    "ToolOutput",
    "UserContentPart",
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
    "mcp",
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
