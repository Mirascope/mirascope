"""The Mirascope OpenAI Module."""

from typing import TypeAlias

from openai.types.chat import ChatCompletionMessageParam

from ..base import BaseMessageParam
from ._call import openai_call
from ._call import openai_call as call
from .call_params import OpenAICallParams
from .call_response import OpenAICallResponse
from .call_response_chunk import OpenAICallResponseChunk
from .dynamic_config import AsyncOpenAIDynamicConfig, OpenAIDynamicConfig
from .stream import OpenAIStream
from .tool import OpenAITool, OpenAIToolConfig

OpenAIMessageParam: TypeAlias = ChatCompletionMessageParam | BaseMessageParam

__all__ = [
    "AsyncOpenAIDynamicConfig",
    "OpenAICallParams",
    "OpenAICallResponse",
    "OpenAICallResponseChunk",
    "OpenAIDynamicConfig",
    "OpenAIMessageParam",
    "OpenAIStream",
    "OpenAITool",
    "OpenAIToolConfig",
    "call",
    "openai_call",
]
