"""The Mirascope Anthropic Module."""

from typing import TypeAlias

from anthropic.types import MessageParam

from ..base import BaseMessageParam
from ._call import anthropic_call
from ._call import anthropic_call as call
from .call_params import AnthropicCallParams
from .call_response import AnthropicCallResponse
from .call_response_chunk import AnthropicCallResponseChunk
from .dynamic_config import AnthropicDynamicConfig, AsyncAnthropicDynamicConfig
from .stream import AnthropicStream
from .tool import AnthropicTool, AnthropicToolConfig

AnthropicMessageParam: TypeAlias = MessageParam | BaseMessageParam

__all__ = [
    "AnthropicCallParams",
    "AnthropicCallResponse",
    "AnthropicCallResponseChunk",
    "AnthropicDynamicConfig",
    "AnthropicMessageParam",
    "AnthropicStream",
    "AnthropicTool",
    "AnthropicToolConfig",
    "AsyncAnthropicDynamicConfig",
    "anthropic_call",
    "call",
]
