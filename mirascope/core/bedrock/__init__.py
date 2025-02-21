from typing import TypeAlias

from .. import BaseMessageParam
from ._call import bedrock_call
from ._call import bedrock_call as call
from ._types import (
    AssistantMessageTypeDef,
    InternalBedrockMessageParam,
    UserMessageTypeDef,
)
from .call_params import BedrockCallParams
from .call_response import BedrockCallResponse
from .call_response_chunk import BedrockCallResponseChunk
from .dynamic_config import AsyncBedrockDynamicConfig, BedrockDynamicConfig
from .stream import BedrockStream
from .tool import BedrockTool, BedrockToolConfig

BedrockMessageParam: TypeAlias = InternalBedrockMessageParam | BaseMessageParam

__all__ = [
    "AssistantMessageTypeDef",
    "AsyncBedrockDynamicConfig",
    "BedrockCallParams",
    "BedrockCallResponse",
    "BedrockCallResponseChunk",
    "BedrockDynamicConfig",
    "BedrockMessageParam",
    "BedrockStream",
    "BedrockTool",
    "BedrockToolConfig",
    "UserMessageTypeDef",
    "bedrock_call",
    "call",
]
