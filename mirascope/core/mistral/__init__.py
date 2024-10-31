"""The Mirascope Mistral Module."""

from typing import TypeAlias

from mistralai.models.chat_completion import ChatMessage

from ..base import BaseMessageParam
from ._call import mistral_call
from ._call import mistral_call as call
from .call_params import MistralCallParams
from .call_response import MistralCallResponse
from .call_response_chunk import MistralCallResponseChunk
from .dynamic_config import AsyncMistralDynamicConfig, MistralDynamicConfig
from .stream import MistralStream
from .tool import MistralTool

MistralMessageParam: TypeAlias = ChatMessage | BaseMessageParam

__all__ = [
    "AsyncMistralDynamicConfig",
    "call",
    "MistralDynamicConfig",
    "MistralCallParams",
    "MistralCallResponse",
    "MistralCallResponseChunk",
    "MistralMessageParam",
    "MistralStream",
    "MistralTool",
    "mistral_call",
]
