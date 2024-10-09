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

InternalBedrockMessageParam: TypeAlias = (
    SyncMessageUnionTypeDef | AsyncMessageUnionTypeDef
)

Roles = Literal["user", "assistant"]


class UserMessageTypeDef(TypedDict):
    role: Literal["user"]
    content: Sequence[ContentBlockUnionTypeDef]


class AssistantMessageTypeDef(TypedDict):
    role: Literal["assistant"]
    content: Sequence[ContentBlockUnionTypeDef]


class StreamOutputChunk(ConverseStreamOutputTypeDef):
    responseMetadata: ResponseMetadataTypeDef
    model: str


class AsyncStreamOutputChunk(AsyncConverseStreamOutputTypeDef):
    responseMetadata: AsyncResponseMetadataTypeDef
    model: str
