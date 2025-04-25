"""The `llm` module for writing provider-agnostic LLM Generations.

This module provides a unified interface for interacting with different LLM providers,
including messages, tools, response formatting, and streaming. It allows you to write
code that works with multiple LLM providers without changing your application logic.
"""

from . import content as content
from .agents import Agent, AsyncAgent, AsyncStructuredAgent, StructuredAgent, agent
from .calls import (
    AsyncCall,
    AsyncStructuredCall,
    Call,
    StructuredCall,
    call,
)
from .content import Content
from .contexts import Context, context, model
from .messages import (
    DynamicConfig,
    Message,
    PromptTemplate,
    assistant,
    prompt_template,
    system,
    user,
)
from .models import LLM, Client, Params
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
    "Call",
    "Client",
    "Content",
    "Context",
    "DynamicConfig",
    "Message",
    "Params",
    "PromptTemplate",
    "Response",
    "ResponseFormat",
    "Stream",
    "StreamChunk",
    "StructuredAgent",
    "StructuredCall",
    "StructuredStream",
    "Tool",
    "ToolDef",
    "agent",
    "assistant",
    "call",
    "content",
    "context",
    "model",
    "prompt_template",
    "response_format",
    "system",
    "tool",
    "user",
]
