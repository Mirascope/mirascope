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
    tools,
    types,
)
from .agents import Agent, AgentTemplate, AsyncAgent, AsyncAgentTemplate, agent
from .calls import call, context_call
from .clients import BaseClient, BaseParams
from .content import (
    AssistantContent,
    Audio,
    Document,
    Image,
    ImageUrl,
    Text,
    TextPartial,
    Thinking,
    ThinkingPartial,
    ToolCall,
    ToolCallPartial,
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
from .responses import AsyncStreamResponse, BaseStreamResponse, Response, StreamResponse
from .tools import Tool, context_tool, tool

__all__ = [
    "LLM",
    "APIError",
    "Agent",
    "AgentTemplate",
    "AssistantContent",
    "AssistantMessage",
    "AsyncAgent",
    "AsyncAgentTemplate",
    "AsyncStreamResponse",
    "AsyncStreamResponse",
    "Audio",
    "AuthenticationError",
    "BadRequestError",
    "BaseClient",
    "BaseParams",
    "BaseStreamResponse",
    "ConnectionError",
    "Context",
    "Document",
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
    "StreamResponse",
    "StreamResponse",
    "SystemMessage",
    "Text",
    "TextPartial",
    "Thinking",
    "ThinkingPartial",
    "TimeoutError",
    "Tool",
    "Tool",
    "ToolCall",
    "ToolCallPartial",
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
    "mcp",
    "messages",
    "model",
    "models",
    "prompts",
    "responses",
    "tool",
    "tools",
    "types",
]
