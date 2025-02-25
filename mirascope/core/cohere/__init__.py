"""The Mirascope Cohere Module."""

from typing import TypeAlias

from cohere.types import ChatMessage, ToolResult

from ..base import BaseMessageParam
from ._call import cohere_call
from ._call import cohere_call as call
from .call_params import CohereCallParams
from .call_response import CohereCallResponse
from .call_response_chunk import CohereCallResponseChunk
from .dynamic_config import AsyncCohereDynamicConfig, CohereDynamicConfig
from .stream import CohereStream
from .tool import CohereTool

CohereMessageParam: TypeAlias = ChatMessage | ToolResult | BaseMessageParam

__all__ = [
    "AsyncCohereDynamicConfig",
    "CohereCallParams",
    "CohereCallResponse",
    "CohereCallResponseChunk",
    "CohereDynamicConfig",
    "CohereMessageParam",
    "CohereStream",
    "CohereTool",
    "call",
    "cohere_call",
]
