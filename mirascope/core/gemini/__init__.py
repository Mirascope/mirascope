"""The Mirascope Gemini Module."""

from typing import TypeAlias

from google.generativeai.protos import FunctionResponse
from google.generativeai.types import ContentDict

from ..base import BaseMessageParam
from ._call import gemini_call
from ._call import gemini_call as call
from .call_params import GeminiCallParams
from .call_response import GeminiCallResponse
from .call_response_chunk import GeminiCallResponseChunk
from .dynamic_config import GeminiDynamicConfig
from .stream import GeminiStream
from .tool import GeminiTool

GeminiMessageParam: TypeAlias = ContentDict | FunctionResponse | BaseMessageParam

__all__ = [
    "call",
    "GeminiDynamicConfig",
    "GeminiCallParams",
    "GeminiCallResponse",
    "GeminiCallResponseChunk",
    "GeminiMessageParam",
    "GeminiStream",
    "GeminiTool",
    "gemini_call",
]
