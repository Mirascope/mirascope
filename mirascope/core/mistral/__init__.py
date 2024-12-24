"""The Mirascope Mistral Module."""

from typing import TypeAlias

from mistralai.models import (
    AssistantMessage,
    SystemMessage,
    ToolMessage,
    UserMessage,
)

from ..base import BaseMessageParam
from ._call import mistral_call
from ._call import mistral_call as call
from .call_params import MistralCallParams
from .call_response import MistralCallResponse
from .call_response_chunk import MistralCallResponseChunk
from .dynamic_config import MistralDynamicConfig
from .stream import MistralStream
from .tool import MistralTool

MistralMessageParam: TypeAlias = (
    AssistantMessage | SystemMessage | ToolMessage | UserMessage | BaseMessageParam
)

__all__ = [
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
