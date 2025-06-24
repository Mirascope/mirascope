"""The `llm` module for writing provider-agnostic LLM Generations.

This module provides a unified interface for interacting with different LLM providers,
including messages, tools, response formatting, and streaming. It allows you to write
code that works with multiple LLM providers without changing your application logic.
"""

from . import (
    agents,
    calls,
    content,
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
from .messages import Message
from .models import LLM, Client, Params, model
from .prompt_templates import (
    DynamicConfig,
    prompt_template,
)
from .response_formatting import ResponseFormat
from .response_formatting.decorator import response_format
from .responses import (
    AsyncStream,
    AsyncStructuredStream,
    Response,
    Stream,
    StreamChunk,
    StructuredStream,
)
from .tools import Tool, ToolDef
from .tools.decorator import tool

__all__ = [
    "LLM",
    "Agent",
    "AsyncAgent",
    "AsyncCall",
    "AsyncStream",
    "AsyncStructuredAgent",
    "AsyncStructuredCall",
    "AsyncStructuredStream",
    "Audio",
    "Call",
    "Client",
    "Content",
    "Context",
    "Document",
    "DynamicConfig",
    "Image",
    "Message",
    "Params",
    "Response",
    "ResponseFormat",
    "Stream",
    "StreamChunk",
    "StructuredAgent",
    "StructuredCall",
    "StructuredStream",
    "Thinking",
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
    "messages",
    "model",
    "models",
    "prompt_template",
    "prompt_templates",
    "response_format",
    "response_formatting",
    "responses",
    "tool",
    "tools",
    "types",
]
