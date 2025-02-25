"""The Mirascope Google Module."""

from typing import TypeAlias

from google.genai.types import ContentDict, FunctionResponse

from ..base import BaseMessageParam
from ._call import google_call
from ._call import google_call as call
from .call_params import GoogleCallParams
from .call_response import GoogleCallResponse
from .call_response_chunk import GoogleCallResponseChunk
from .dynamic_config import GoogleDynamicConfig
from .stream import GoogleStream
from .tool import GoogleTool

GoogleMessageParam: TypeAlias = ContentDict | FunctionResponse | BaseMessageParam

__all__ = [
    "GoogleCallParams",
    "GoogleCallResponse",
    "GoogleCallResponseChunk",
    "GoogleDynamicConfig",
    "GoogleMessageParam",
    "GoogleStream",
    "GoogleTool",
    "call",
    "google_call",
]
