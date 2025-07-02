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
    prompt_templates,
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
from .content import (
    Audio,
    Content,
    Document,
    Image,
    Thinking,
    ToolCall,
    ToolOutput,
    Video,
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
from .messages import Message, Prompt
from .models import LLM, Client, Params, model
from .prompt_templates import prompt_template
from .response_formatting import ResponseFormat
from .response_formatting.decorator import response_format
from .responses import (
    AsyncStream,
    AsyncStructuredStream,
    BaseResponse,
    ContextResponse,
    Response,
    Stream,
    StreamChunk,
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
    "AuthenticationError",
    "BadRequestError",
    "Call",
    "Client",
    "ConnectionError",
    "Content",
    "Context",
    "ContextResponse",
    "Document",
    "Image",
    "Message",
    "MirascopeError",
    "NotFoundError",
    "Params",
    "PermissionError",
    "Prompt",
    "RateLimitError",
    "BaseResponse",
    "ResponseFormat",
    "ServerError",
    "Response",
    "Stream",
    "StreamChunk",
    "StructuredAgent",
    "StructuredCall",
    "StructuredStream",
    "Thinking",
    "TimeoutError",
    "Tool",
    "ToolCall",
    "ToolDef",
    "ToolOutput",
    "Video",
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
    "prompt_templates",
    "response_format",
    "response_formatting",
    "responses",
    "tool",
    "tools",
    "types",
]
