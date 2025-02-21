"""The Mirascope xAI Module."""

from typing import TypeAlias

from ..openai import OpenAIMessageParam
from ._call import xai_call
from ._call import xai_call as call
from .call_params import XAICallParams
from .call_response import XAICallResponse
from .call_response_chunk import XAICallResponseChunk
from .dynamic_config import AsyncXAIDynamicConfig, XAIDynamicConfig
from .stream import XAIStream
from .tool import XAITool

XAIMessageParam: TypeAlias = OpenAIMessageParam

__all__ = [
    "AsyncXAIDynamicConfig",
    "XAICallParams",
    "XAICallResponse",
    "XAICallResponseChunk",
    "XAIDynamicConfig",
    "XAIMessageParam",
    "XAIStream",
    "XAITool",
    "call",
    "xai_call",
]
