"""The Mirascope LiteLLM Module."""

from typing import TypeAlias

from ..openai import OpenAIMessageParam
from ._call import litellm_call
from ._call import litellm_call as call
from .call_params import LiteLLMCallParams
from .call_response import LiteLLMCallResponse
from .call_response_chunk import LiteLLMCallResponseChunk
from .dynamic_config import AsyncLiteLLMDynamicConfig, LiteLLMDynamicConfig
from .stream import LiteLLMStream
from .tool import LiteLLMTool

LiteLLMMessageParam: TypeAlias = OpenAIMessageParam

__all__ = [
    "AsyncLiteLLMDynamicConfig",
    "LiteLLMCallParams",
    "LiteLLMCallResponse",
    "LiteLLMCallResponseChunk",
    "LiteLLMDynamicConfig",
    "LiteLLMMessageParam",
    "LiteLLMStream",
    "LiteLLMTool",
    "call",
    "litellm_call",
]
