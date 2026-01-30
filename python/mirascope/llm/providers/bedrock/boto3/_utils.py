"""Bedrock boto3 provider utilities."""

from __future__ import annotations

import base64
import json
from collections.abc import Iterator, Mapping, Sequence
from typing import TYPE_CHECKING, Any, Literal, TypedDict, cast
from typing_extensions import Required

from botocore.exceptions import BotoCoreError, ClientError

from ....content import (
    ContentPart,
    Text,
    TextChunk,
    TextEndChunk,
    TextStartChunk,
    ToolCall,
    ToolCallChunk,
    ToolCallEndChunk,
    ToolCallStartChunk,
)
from ....exceptions import (
    BadRequestError,
    FeatureNotSupportedError,
    NotFoundError,
    PermissionError,
    ProviderError,
    RateLimitError,
    ServerError,
)
from ....formatting import Format, FormattableT, OutputParser, resolve_format
from ....messages import AssistantMessage, Message, UserMessage, assistant
from ....responses import ChunkIterator, FinishReason, Usage
from ....tools import FORMAT_TOOL_NAME, AnyToolSchema, BaseToolkit, ProviderTool
from ...base import _utils as _base_utils
from .. import _utils as bedrock_utils
from ..model_id import BedrockModelId

if TYPE_CHECKING:
    from ....models import Params

DEFAULT_MAX_TOKENS = 4096
DEFAULT_FORMAT_MODE = "tool"

BEDROCK_BOTO3_PROVIDER_ID = "bedrock:boto3"

# Bedrock Converse API type definitions.
# See: https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html

ImageFormat = Literal["png", "jpeg", "gif", "webp"]


class ImageSource(TypedDict, total=False):
    """Image source with bytes data."""

    bytes: bytes


class ImageBlock(TypedDict):
    """Image content block."""

    format: ImageFormat
    source: ImageSource


class ToolInputSchema(TypedDict):
    """Tool input JSON schema."""

    json: dict[str, Any]


class ToolSpecification(TypedDict, total=False):
    """Tool specification."""

    name: Required[str]
    inputSchema: Required[ToolInputSchema]
    description: str


class Tool(TypedDict, total=False):
    """Tool definition."""

    toolSpec: ToolSpecification


class SpecificToolChoice(TypedDict):
    """Specific tool choice by name."""

    name: str


class ToolChoice(TypedDict, total=False):
    """Tool choice configuration (tagged union)."""

    auto: dict[str, Any]
    any: dict[str, Any]
    tool: SpecificToolChoice


class ToolConfiguration(TypedDict, total=False):
    """Tool configuration for converse request."""

    tools: list[Tool]
    toolChoice: ToolChoice


class ToolUseBlock(TypedDict):
    """Tool use request from the model."""

    toolUseId: str
    name: str
    input: dict[str, Any]


class ToolResultContentBlock(TypedDict, total=False):
    """Content block within a tool result."""

    text: str


ToolResultStatus = Literal["success", "error"]


class ToolResultBlock(TypedDict, total=False):
    """Tool result to send back to the model."""

    toolUseId: str
    content: list[ToolResultContentBlock]
    status: ToolResultStatus


class ContentBlock(TypedDict, total=False):
    """Content block in a message (tagged union)."""

    text: str
    image: ImageBlock
    toolUse: ToolUseBlock
    toolResult: ToolResultBlock


MessageRole = Literal["user", "assistant"]


class ConverseMessage(TypedDict):
    """A message in the conversation."""

    role: MessageRole
    content: list[ContentBlock]


class SystemContentBlock(TypedDict, total=False):
    """System content block (tagged union)."""

    text: str


class InferenceConfiguration(TypedDict, total=False):
    """Inference configuration parameters."""

    maxTokens: int
    temperature: float
    topP: float
    stopSequences: list[str]


class ConverseKwargs(TypedDict, total=False):
    """Kwargs for Bedrock Runtime converse method."""

    modelId: str
    messages: list[ConverseMessage]
    system: list[SystemContentBlock]
    toolConfig: ToolConfiguration
    inferenceConfig: InferenceConfiguration


class TokenUsage(TypedDict, total=False):
    """Token usage information."""

    inputTokens: int
    outputTokens: int


class ConverseMetrics(TypedDict, total=False):
    """Metrics from the converse call."""

    latencyMs: int


class ConverseOutput(TypedDict, total=False):
    """Output from the converse call."""

    message: ConverseMessage


StopReason = Literal[
    "end_turn",
    "tool_use",
    "max_tokens",
    "stop_sequence",
    "content_filtered",
    "guardrail_intervened",
]


class ConverseResponse(TypedDict, total=False):
    """Response from Bedrock Runtime converse method."""

    output: ConverseOutput
    stopReason: StopReason
    usage: TokenUsage
    metrics: ConverseMetrics


class ToolUseBlockStart(TypedDict):
    """Partial tool use in stream start event (without input)."""

    toolUseId: str
    name: str


class ContentBlockStart(TypedDict, total=False):
    """Content block start event data."""

    toolUse: ToolUseBlockStart


class ContentBlockStartEvent(TypedDict, total=False):
    """Content block start event."""

    contentBlockIndex: int
    start: ContentBlockStart


class TextDelta(TypedDict, total=False):
    """Text delta in streaming."""

    text: str


class ToolUseDelta(TypedDict, total=False):
    """Tool use delta in streaming."""

    input: str


class ContentBlockDelta(TypedDict, total=False):
    """Content block delta data (tagged union)."""

    text: str
    toolUse: ToolUseDelta


class ContentBlockDeltaEvent(TypedDict, total=False):
    """Content block delta event."""

    contentBlockIndex: int
    delta: ContentBlockDelta


class ContentBlockStopEvent(TypedDict, total=False):
    """Content block stop event."""

    contentBlockIndex: int


class MessageStopEvent(TypedDict, total=False):
    """Message stop event."""

    stopReason: StopReason


class StreamMetadata(TypedDict, total=False):
    """Metadata in stream events."""

    usage: TokenUsage
    metrics: ConverseMetrics


class ConverseStreamEvent(TypedDict, total=False):
    """Stream event from Bedrock Runtime converseStream (tagged union)."""

    contentBlockStart: ContentBlockStartEvent
    contentBlockDelta: ContentBlockDeltaEvent
    contentBlockStop: ContentBlockStopEvent
    messageStop: MessageStopEvent
    metadata: StreamMetadata


def get_error_type_from_code(
    error_code: str,
) -> type[ProviderError]:
    error_map: dict[str, type[ProviderError]] = {
        "AccessDeniedException": PermissionError,
        "ValidationException": BadRequestError,
        "ResourceNotFoundException": NotFoundError,
        "ThrottlingException": RateLimitError,
        "ServiceUnavailableException": ServerError,
        "ModelNotReadyException": ServerError,
        "InternalServerException": ServerError,
    }
    return error_map.get(error_code, ProviderError)


def get_error_type_from_client_error(e: ClientError) -> type[ProviderError]:
    response = cast(Mapping[str, object], e.response)
    error = response.get("Error")
    error_code = ""
    if isinstance(error, Mapping):
        error_map = cast(Mapping[str, object], error)
        code = error_map.get("Code")
        if isinstance(code, str):
            error_code = code
    return get_error_type_from_code(error_code)


BEDROCK_BOTO3_ERROR_MAP: dict[type[Exception], Any] = {
    ClientError: get_error_type_from_client_error,
    BotoCoreError: ProviderError,
}


STOP_REASON_MAP: dict[str, FinishReason] = {
    "max_tokens": FinishReason.MAX_TOKENS,
    "content_filtered": FinishReason.REFUSAL,
    "guardrail_intervened": FinishReason.REFUSAL,
}


def _normalize_tool_name(name: str) -> str:
    format_tool_token = FORMAT_TOOL_NAME.lstrip("_")
    if name.lstrip("_") == format_tool_token:
        return FORMAT_TOOL_NAME
    return name


def _encode_content_part(part: ContentPart) -> ContentBlock:
    """Encode a content part to a Bedrock ContentBlock.

    Args:
        part: The content part to encode.

    Returns:
        A ContentBlock dictionary.
    """
    if part.type == "text":
        return ContentBlock(text=part.text)
    elif part.type == "image":
        if part.source.type == "base64_image_source":
            format_map: dict[str, ImageFormat] = {
                "image/jpeg": "jpeg",
                "image/png": "png",
                "image/gif": "gif",
                "image/webp": "webp",
            }
            image_format: ImageFormat = format_map.get(part.source.mime_type, "jpeg")
            return ContentBlock(
                image=ImageBlock(
                    format=image_format,
                    source=ImageSource(bytes=base64.b64decode(part.source.data)),
                )
            )
        else:
            raise FeatureNotSupportedError(
                "url image input",
                provider_id=BEDROCK_BOTO3_PROVIDER_ID,
                message=(
                    "Bedrock Converse API does not support URL image sources. "
                    "Use Image.download() to convert the URL to base64 first."
                ),
            )
    elif part.type == "tool_output":
        return ContentBlock(
            toolResult=ToolResultBlock(
                toolUseId=part.id,
                content=[ToolResultContentBlock(text=str(part.result))],
            )
        )
    elif part.type == "tool_call":
        return ContentBlock(
            toolUse=ToolUseBlock(
                toolUseId=part.id,
                name=part.name,
                input=json.loads(part.args),
            )
        )
    elif part.type == "thought":
        return ContentBlock(text=f"**Thinking:** {part.thought}")
    elif part.type == "audio":
        raise FeatureNotSupportedError(
            "audio input",
            provider_id=BEDROCK_BOTO3_PROVIDER_ID,
            message="Bedrock Converse API does not support audio input.",
        )
    elif part.type == "document":
        raise FeatureNotSupportedError(
            "document input",
            provider_id=BEDROCK_BOTO3_PROVIDER_ID,
            message="Bedrock Converse API document support is not implemented.",
        )
    else:  # pragma: no cover
        raise ValueError(f"Unsupported content type: {part.type}")


def _encode_message(
    message: UserMessage | AssistantMessage,
) -> ConverseMessage:
    """Encode a message to a Bedrock ConverseMessage.

    Args:
        message: The message to encode.

    Returns:
        A ConverseMessage dictionary.
    """
    content_blocks: list[ContentBlock] = []
    for part in message.content:
        content_blocks.append(_encode_content_part(part))
    return ConverseMessage(role=message.role, content=content_blocks)


def _encode_messages(
    messages: Sequence[UserMessage | AssistantMessage],
) -> list[ConverseMessage]:
    """Encode a sequence of messages to Bedrock ConverseMessages.

    Args:
        messages: The messages to encode.

    Returns:
        A list of ConverseMessage dictionaries.
    """
    return [_encode_message(msg) for msg in messages]


def _encode_tool(tool: AnyToolSchema | ProviderTool) -> Tool:
    """Encode a tool schema to a Bedrock Tool.

    Args:
        tool: The tool schema to encode.

    Returns:
        A Tool dictionary.
    """
    if isinstance(tool, ProviderTool):
        raise FeatureNotSupportedError(
            f"Provider tool {tool.name}",
            provider_id=BEDROCK_BOTO3_PROVIDER_ID,
        )
    schema_dict = tool.parameters.model_dump(by_alias=True, exclude_none=True)
    schema_dict["type"] = "object"
    return Tool(
        toolSpec=ToolSpecification(
            name=tool.name,
            description=tool.description or "",
            inputSchema=ToolInputSchema(json=schema_dict),
        )
    )


def encode_request(
    *,
    model_id: BedrockModelId,
    messages: Sequence[Message],
    toolkit: BaseToolkit[AnyToolSchema],
    format: type[FormattableT]
    | Format[FormattableT]
    | OutputParser[FormattableT]
    | None,
    params: Params,
) -> tuple[Sequence[Message], Format[FormattableT] | None, ConverseKwargs]:
    """Prepare a request for the Bedrock Runtime converse method.

    Args:
        model_id: The Bedrock model ID.
        messages: The messages to send.
        toolkit: Toolkit for the model.
        format: Optional output format.
        params: Additional parameters.

    Returns:
        Tuple of (input_messages, resolved_format, kwargs).
    """
    inference_config: InferenceConfiguration = {}

    with _base_utils.ensure_all_params_accessed(
        params=params,
        provider_id="bedrock:boto3",
        unsupported_params=["thinking", "seed", "top_k"],
    ) as param_accessor:
        if param_accessor.temperature is not None:
            inference_config["temperature"] = param_accessor.temperature
        if param_accessor.max_tokens is not None:
            inference_config["maxTokens"] = param_accessor.max_tokens
        else:
            inference_config["maxTokens"] = DEFAULT_MAX_TOKENS
        if param_accessor.top_p is not None:
            inference_config["topP"] = param_accessor.top_p
        if param_accessor.stop_sequences is not None:
            inference_config["stopSequences"] = param_accessor.stop_sequences

    tools = toolkit.tools

    if _base_utils.has_strict_tools(tools):
        raise FeatureNotSupportedError(
            feature="strict tools",
            provider_id=BEDROCK_BOTO3_PROVIDER_ID,
            model_id=model_id,
            message="Bedrock Converse API does not support strict tools.",
        )

    converse_tools: list[Tool] = [_encode_tool(tool) for tool in tools]

    format = resolve_format(format, default_mode=DEFAULT_FORMAT_MODE)
    if format is not None:
        if format.mode == "strict":
            raise FeatureNotSupportedError(
                feature="formatting_mode:strict",
                provider_id=BEDROCK_BOTO3_PROVIDER_ID,
                model_id=model_id,
                message="Bedrock Converse API does not support strict formatting mode.",
            )

        if format.mode == "tool":
            format_tool_schema = format.create_tool_schema()
            converse_tools.append(_encode_tool(format_tool_schema))

        if format.formatting_instructions:
            messages = _base_utils.add_system_instructions(
                messages, format.formatting_instructions
            )

    system_message_content, remaining_messages = _base_utils.extract_system_message(
        messages
    )

    kwargs: ConverseKwargs = {
        "modelId": bedrock_utils.bedrock_model_name(model_id),
        "messages": _encode_messages(remaining_messages),
        "inferenceConfig": inference_config,
    }

    if system_message_content:
        kwargs["system"] = [SystemContentBlock(text=system_message_content)]

    if converse_tools:
        tool_config: ToolConfiguration = ToolConfiguration(tools=converse_tools)
        if format is not None and format.mode == "tool" and not tools:
            tool_config["toolChoice"] = ToolChoice(
                tool=SpecificToolChoice(name=FORMAT_TOOL_NAME)
            )
        elif format is not None and format.mode == "tool" and tools:
            tool_config["toolChoice"] = ToolChoice(any={})
        kwargs["toolConfig"] = tool_config

    return messages, format, kwargs


def decode_response(
    response: ConverseResponse,
    model_id: BedrockModelId,
    *,
    provider_id: str = BEDROCK_BOTO3_PROVIDER_ID,
) -> tuple[AssistantMessage, FinishReason | None, Usage]:
    """Decode a Bedrock Converse response.

    Args:
        response: The raw response from Bedrock Converse.
        model_id: The model ID used.
        provider_id: The provider ID to use in the assistant message.

    Returns:
        Tuple of (assistant_message, finish_reason, usage).
    """
    output: ConverseOutput = response.get("output", {})
    message: ConverseMessage = output.get("message", {})  # type: ignore[assignment]
    content_blocks: list[ContentBlock] = message.get("content", [])
    stop_reason: StopReason | str = response.get("stopReason", "")
    usage_data: TokenUsage = response.get("usage", {})

    content_parts: list[Text | ToolCall] = []

    for block in content_blocks:
        if "text" in block:
            content_parts.append(Text(text=block["text"]))
        elif "toolUse" in block:
            tool_use = block["toolUse"]
            tool_name = _normalize_tool_name(tool_use.get("name", ""))
            content_parts.append(
                ToolCall(
                    id=tool_use.get("toolUseId", ""),
                    name=tool_name,
                    args=json.dumps(tool_use.get("input", {})),
                )
            )

    finish_reason: FinishReason | None = STOP_REASON_MAP.get(stop_reason)

    usage = Usage(
        input_tokens=usage_data.get("inputTokens", 0),
        output_tokens=usage_data.get("outputTokens", 0),
    )

    assistant_message = assistant(
        content=content_parts if content_parts else [Text(text="")],
        model_id=model_id,
        provider_id=provider_id,
        provider_model_name=bedrock_utils.bedrock_model_name(model_id),
        raw_message=None,
    )

    return assistant_message, finish_reason, usage


def decode_stream(
    event_stream: Iterator[ConverseStreamEvent],
) -> ChunkIterator:
    """Decode a Bedrock ConverseStream response.

    Args:
        event_stream: The event stream from Bedrock ConverseStream.

    Yields:
        StreamResponseChunk objects.
    """
    text_started = False
    current_tool_use_id: str | None = None

    for event in event_stream:
        if "contentBlockStart" in event:
            content_block_start: ContentBlockStartEvent = event["contentBlockStart"]
            start: ContentBlockStart = content_block_start.get("start", {})
            if "toolUse" in start:
                tool_use: ToolUseBlockStart = start["toolUse"]
                tool_use_id: str = tool_use.get("toolUseId", "")
                tool_name: str = _normalize_tool_name(tool_use.get("name", ""))
                current_tool_use_id = tool_use_id
                yield ToolCallStartChunk(
                    id=tool_use_id,
                    name=tool_name,
                )
            else:
                text_started = True
                yield TextStartChunk()

        elif "contentBlockDelta" in event:
            content_block_delta: ContentBlockDeltaEvent = event["contentBlockDelta"]
            delta: ContentBlockDelta = content_block_delta.get("delta", {})
            if "text" in delta:
                # Some models (e.g., Amazon Nova) don't emit contentBlockStart
                # for text blocks. Emit TextStartChunk if not already started.
                if not text_started:
                    text_started = True
                    yield TextStartChunk()
                yield TextChunk(delta=delta["text"])
            elif "toolUse" in delta and current_tool_use_id is not None:
                tool_use_delta: ToolUseDelta = delta["toolUse"]
                yield ToolCallChunk(
                    id=current_tool_use_id,
                    delta=tool_use_delta.get("input", ""),
                )

        elif "contentBlockStop" in event:
            if current_tool_use_id is not None:
                yield ToolCallEndChunk(id=current_tool_use_id)
                current_tool_use_id = None
            elif text_started:
                yield TextEndChunk()
                text_started = False

        elif "messageStop" in event:
            message_stop: MessageStopEvent = event["messageStop"]
            stop_reason: StopReason | str = message_stop.get("stopReason", "")
            finish_reason = STOP_REASON_MAP.get(stop_reason)
            if finish_reason is not None:
                from ....responses import FinishReasonChunk

                yield FinishReasonChunk(finish_reason=finish_reason)

        elif "metadata" in event:
            metadata: StreamMetadata = event["metadata"]
            usage_data: TokenUsage = metadata.get("usage", {})
            from ....responses import UsageDeltaChunk

            yield UsageDeltaChunk(
                input_tokens=usage_data.get("inputTokens", 0),
                output_tokens=usage_data.get("outputTokens", 0),
            )
