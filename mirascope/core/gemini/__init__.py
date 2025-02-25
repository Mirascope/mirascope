"""The Mirascope Gemini Module."""

import inspect
import warnings
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

warnings.warn(
    inspect.cleandoc("""
    The `mirascope.core.gemini` module is deprecated and will be removed in a future release.
    Please use the `mirascope.core.google` module instead.
    """),
    category=DeprecationWarning,
)

__all__ = [
    "GeminiCallParams",
    "GeminiCallResponse",
    "GeminiCallResponseChunk",
    "GeminiDynamicConfig",
    "GeminiMessageParam",
    "GeminiStream",
    "GeminiTool",
    "call",
    "gemini_call",
]
