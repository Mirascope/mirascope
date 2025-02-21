"""The Mirascope Vertex Module."""

import inspect
import warnings
from typing import TypeAlias

from google.cloud.aiplatform_v1beta1.types import FunctionResponse
from vertexai.generative_models import Content

from ..base import BaseMessageParam
from ._call import vertex_call
from ._call import vertex_call as call
from .call_params import VertexCallParams
from .call_response import VertexCallResponse
from .call_response_chunk import VertexCallResponseChunk
from .dynamic_config import VertexDynamicConfig
from .stream import VertexStream
from .tool import VertexTool

VertexMessageParam: TypeAlias = Content | FunctionResponse | BaseMessageParam

warnings.warn(
    inspect.cleandoc("""
    The `mirascope.core.gemini` module is deprecated and will be removed in a future release.
    Please use the `mirascope.core.google` module instead.
                     
    You can use Vertex AI by setting a custom `client` or environment variables.
    See these docs for reference:
        - Google AI SDK Custom Client: https://googleapis.github.io/python-genai/#create-a-client
        - Mirascope Google Custom Client: https://mirascope.com/learn/calls/#__tabbed_39_5
    """),
    category=DeprecationWarning,
)

__all__ = [
    "VertexCallParams",
    "VertexCallResponse",
    "VertexCallResponseChunk",
    "VertexDynamicConfig",
    "VertexMessageParam",
    "VertexStream",
    "VertexTool",
    "call",
    "vertex_call",
]
