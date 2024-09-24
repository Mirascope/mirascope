"""The Mirascope OpenAI Module."""

from typing import TypeAlias

from openai.types.chat import ChatCompletionMessageParam

from ._call import openai_call
from ._call import openai_call as call
from .batch import OpenAIBatch
from .call_params import OpenAICallParams
from .call_response import OpenAICallResponse
from .call_response_chunk import OpenAICallResponseChunk
from .dynamic_config import OpenAIDynamicConfig
from .stream import OpenAIStream
from .tool import OpenAITool, OpenAIToolConfig

OpenAIMessageParam: TypeAlias = ChatCompletionMessageParam

__all__ = [
    "call",
    "OpenAIDynamicConfig",
    "OpenAICallParams",
    "OpenAICallResponse",
    "OpenAICallResponseChunk",
    "OpenAIMessageParam",
    "OpenAIStream",
    "OpenAITool",
    "OpenAIToolConfig",
    "openai_call",
    "OpenAIBatch",
]
