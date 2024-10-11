from typing import Literal, TypeAlias

from mypy_boto3_bedrock_runtime.literals import (
    ConversationRoleType as SyncConversationRoleType,
)
from mypy_boto3_bedrock_runtime.type_defs import (
    ContentBlockOutputTypeDef as SyncContentBlockOutputTypeDef,
)
from mypy_boto3_bedrock_runtime.type_defs import (
    ConverseStreamOutputTypeDef,
    ResponseMetadataTypeDef,
    ToolResultBlockOutputTypeDef,
    ToolUseBlockOutputTypeDef,
)
from mypy_boto3_bedrock_runtime.type_defs import (
    TokenUsageTypeDef as SyncTokenUsageTypeDef,
)
from mypy_boto3_bedrock_runtime.type_defs import (
    ToolTypeDef as SyncToolTypeDef,
)
from types_aiobotocore_bedrock_runtime.literals import (
    ConversationRoleType as AsyncConversationRoleType,
)
from types_aiobotocore_bedrock_runtime.type_defs import (
    ContentBlockOutputTypeDef as AsyncContentBlockOutputTypeDef,
)
from types_aiobotocore_bedrock_runtime.type_defs import (
    ConverseStreamOutputTypeDef as AsyncConverseStreamOutputTypeDef,
)
from types_aiobotocore_bedrock_runtime.type_defs import (
    ResponseMetadataTypeDef as AsyncResponseMetadataTypeDef,
)
from types_aiobotocore_bedrock_runtime.type_defs import (
    TokenUsageTypeDef as AsyncTokenUsageTypeDef,
)
from types_aiobotocore_bedrock_runtime.type_defs import (
    ToolTypeDef as AsyncToolTypeDef,
)
from types_aiobotocore_bedrock_runtime.type_defs import (
    ToolUseBlockOutputTypeDef as AsyncToolUseBlockOutputTypeDef,
)
from typing_extensions import TypedDict

TokenUsageTypeDef: TypeAlias = SyncTokenUsageTypeDef | AsyncTokenUsageTypeDef
ConversationRoleType: TypeAlias = SyncConversationRoleType | AsyncConversationRoleType
ContentBlockOutputTypeDef: TypeAlias = (
    SyncContentBlockOutputTypeDef | AsyncContentBlockOutputTypeDef
)
ToolTypeDef: TypeAlias = SyncToolTypeDef | AsyncToolTypeDef


class ToolUseBlockContentTypeDef(TypedDict):
    toolUse: ToolUseBlockOutputTypeDef | AsyncToolUseBlockOutputTypeDef


class ToolUseBlockMessageTypeDef(TypedDict):
    role: ConversationRoleType
    content: list[ToolUseBlockContentTypeDef]


class ToolResultBlockContentTypeDef(TypedDict):
    toolResult: ToolResultBlockOutputTypeDef


class ToolResultBlockMessageTypeDef(TypedDict):
    role: ConversationRoleType
    content: list[ToolResultBlockContentTypeDef]


class AsyncMessageTypeDef(TypedDict):
    role: AsyncConversationRoleType
    content: list[AsyncContentBlockOutputTypeDef]


class SyncMessageTypeDef(TypedDict):
    role: SyncConversationRoleType
    content: list[SyncContentBlockOutputTypeDef]


MessageTypeDef: TypeAlias = SyncMessageTypeDef | AsyncMessageTypeDef

InternalBedrockMessageParam: TypeAlias = (
    MessageTypeDef | ToolResultBlockMessageTypeDef | ToolUseBlockMessageTypeDef
)


class UserMessageTypeDef(TypedDict):
    role: Literal["user"]
    content: list[SyncContentBlockOutputTypeDef]


class AssistantMessageTypeDef(TypedDict):
    role: ConversationRoleType
    content: list[SyncContentBlockOutputTypeDef]


class StreamOutputChunk(ConverseStreamOutputTypeDef):
    responseMetadata: ResponseMetadataTypeDef
    model: str


class AsyncStreamOutputChunk(AsyncConverseStreamOutputTypeDef):
    responseMetadata: AsyncResponseMetadataTypeDef
    model: str
