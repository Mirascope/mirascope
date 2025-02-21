"""The Mirascope Groq Module."""

from typing import TypeAlias

from groq.types.chat import ChatCompletionMessageParam

from ..base import BaseMessageParam
from ._call import groq_call
from ._call import groq_call as call
from .call_params import GroqCallParams
from .call_response import GroqCallResponse
from .call_response_chunk import GroqCallResponseChunk
from .dynamic_config import AsyncGroqDynamicConfig, GroqDynamicConfig
from .stream import GroqStream
from .tool import GroqTool

GroqMessageParam: TypeAlias = ChatCompletionMessageParam | BaseMessageParam

__all__ = [
    "AsyncGroqDynamicConfig",
    "GroqCallParams",
    "GroqCallResponse",
    "GroqCallResponseChunk",
    "GroqDynamicConfig",
    "GroqMessageParam",
    "GroqStream",
    "GroqTool",
    "call",
    "groq_call",
]
