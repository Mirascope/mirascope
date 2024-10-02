"""The Mirascope LiteLLM Module."""

from typing import TypeAlias

from ..openai import (
    OpenAICallResponse,
    OpenAICallResponseChunk,
    OpenAIDynamicConfig,
    OpenAIMessageParam,
)
from ._call import litellm_call
from ._call import litellm_call as call

LiteLLMMessageParam: TypeAlias = OpenAIMessageParam

__all__ = ["call", "LiteLLMMessageParam", "litellm_call"]
