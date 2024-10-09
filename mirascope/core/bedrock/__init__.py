from collections.abc import Sequence
from typing import Literal, TypeAlias

from mypy_boto3_bedrock_runtime.type_defs import (
    ContentBlockUnionTypeDef,
    ConverseStreamOutputTypeDef,
    ResponseMetadataTypeDef,
)
from mypy_boto3_bedrock_runtime.type_defs import (
    MessageUnionTypeDef as SyncMessageUnionTypeDef,
)
from types_aiobotocore_bedrock_runtime.type_defs import (
    ConverseStreamOutputTypeDef as AsyncConverseStreamOutputTypeDef,
)
from types_aiobotocore_bedrock_runtime.type_defs import (
    MessageUnionTypeDef as AsyncMessageUnionTypeDef,
)
from types_aiobotocore_bedrock_runtime.type_defs import (
    ResponseMetadataTypeDef as AsyncResponseMetadataTypeDef,
)
from typing_extensions import TypedDict

from ._call import bedrock_call
from ._call import bedrock_call as call
from ._types import AssistantMessageTypeDef, BedrockMessageParam, UserMessageTypeDef
from .call_params import BedrockCallParams
from .call_response import BedrockCallResponse
from .call_response_chunk import BedrockCallResponseChunk
from .dynamic_config import BedrockDynamicConfig
from .stream import BedrockStream
from .tool import BedrockTool, BedrockToolConfig

__all__ = [
    "AssistantMessageTypeDef",
    "bedrock_call",
    "BedrockCallParams",
    "BedrockCallResponse",
    "BedrockCallResponseChunk",
    "BedrockDynamicConfig",
    "BedrockMessageParam",
    "BedrockStream",
    "BedrockTool",
    "BedrockToolConfig",
    "call",
    "UserMessageTypeDef",
]
