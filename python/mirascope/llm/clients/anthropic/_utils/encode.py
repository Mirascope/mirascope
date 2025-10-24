"""Anthropic message encoding and request preparation."""

import json
from collections.abc import Sequence
from functools import lru_cache
from typing import Literal, TypedDict, cast
from typing_extensions import Required

from anthropic import Omit, types as anthropic_types

from ....content import ContentPart, ImageMimeType
from ....exceptions import FeatureNotSupportedError, FormattingModeNotSupportedError
from ....formatting import (
    Format,
    FormattableT,
    _utils as _formatting_utils,
    resolve_format,
)
from ....messages import AssistantMessage, Message, UserMessage
from ....tools import FORMAT_TOOL_NAME, BaseToolkit, ToolSchema
from ...base import Params, _utils as _base_utils
from ..model_ids import AnthropicModelId

DEFAULT_MAX_TOKENS = 16000

AnthropicImageMimeType = Literal["image/jpeg", "image/png", "image/gif", "image/webp"]


def encode_image_mime_type(
    mime_type: ImageMimeType,
) -> AnthropicImageMimeType:
    """Convert an ImageMimeType into anthropic supported mime type"""
    if mime_type in ("image/jpeg", "image/png", "image/gif", "image/webp"):
        return mime_type
    raise FeatureNotSupportedError(
        feature=f"Image with mime_type: {mime_type}", provider="anthropic"
    )  # pragma: no cover


def _pretty_provider_name(
    provider: Literal["anthropic", "anthropic-bedrock", "anthropic-vertex"],
) -> str:
    """Convert provider string to a pretty name for user-facing messages."""
    if provider == "anthropic-bedrock":
        return "Anthropic Bedrock"
    elif provider == "anthropic-vertex":
        return "Anthropic Vertex AI"
    else:
        return "Anthropic"


class MessageCreateKwargs(TypedDict, total=False):
    """Kwargs for Anthropic Message.create method."""

    model: Required[str]
    max_tokens: Required[int]
    messages: Sequence[anthropic_types.MessageParam]
    system: str | Omit
    tools: Sequence[anthropic_types.ToolParam] | Omit
    tool_choice: anthropic_types.ToolChoiceParam | Omit
    temperature: float | Omit
    top_p: float | Omit
    top_k: int | Omit
    stop_sequences: list[str] | Omit
    thinking: anthropic_types.ThinkingConfigParam | Omit


def _encode_content(
    content: Sequence[ContentPart],
    encode_thoughts: bool,
    provider: Literal["anthropic", "anthropic-bedrock", "anthropic-vertex"],
) -> str | Sequence[anthropic_types.ContentBlockParam]:
    """Returns encoded Anthropic content blocks from mirascope content."""
    if len(content) == 1 and content[0].type == "text":
        return content[0].text

    blocks: list[anthropic_types.ContentBlockParam] = []

    for part in content:
        if part.type == "text":
            blocks.append(anthropic_types.TextBlockParam(type="text", text=part.text))
        elif part.type == "image":
            source: (
                anthropic_types.Base64ImageSourceParam
                | anthropic_types.URLImageSourceParam
            )
            if part.source.type == "base64_image_source":
                source = anthropic_types.Base64ImageSourceParam(
                    type="base64",
                    media_type=encode_image_mime_type(part.source.mime_type),
                    data=part.source.data,
                )
            else:
                if provider in ("anthropic-bedrock", "anthropic-vertex"):
                    raise FeatureNotSupportedError(
                        "url_image_source",
                        provider,
                        message=f"{_pretty_provider_name(provider)} does not support URL-referenced images. Try `llm.Image.download(...)` or `llm.Image.download_async(...)`",
                    )
                source = anthropic_types.URLImageSourceParam(
                    type="url",
                    url=part.source.url,
                )
            blocks.append(anthropic_types.ImageBlockParam(type="image", source=source))
        elif part.type == "tool_output":
            blocks.append(
                anthropic_types.ToolResultBlockParam(
                    type="tool_result",
                    tool_use_id=part.id,
                    content=str(part.value),
                )
            )
        elif part.type == "tool_call":
            blocks.append(
                anthropic_types.ToolUseBlockParam(
                    type="tool_use",
                    id=part.id,
                    name=part.name,
                    input=json.loads(part.args),
                )
            )
        elif part.type == "thought":
            if encode_thoughts:
                blocks.append(
                    anthropic_types.TextBlockParam(
                        type="text", text="**Thinking:** " + part.thought
                    )
                )
        elif part.type == "audio":
            raise FeatureNotSupportedError(
                "audio input",
                provider,
                message=f"{_pretty_provider_name(provider)} does not support audio inputs.",
            )
        else:
            raise NotImplementedError(f"Content type {part.type} not supported")

    return blocks


def _encode_message(
    message: UserMessage | AssistantMessage,
    model_id: AnthropicModelId,
    encode_thoughts: bool,
    provider: Literal["anthropic", "anthropic-bedrock", "anthropic-vertex"],
) -> anthropic_types.MessageParam:
    """Returns Anthropic MessageParam from mirascope Message."""
    if (
        message.role == "assistant"
        and message.provider in ("anthropic", "anthropic-bedrock", "anthropic-vertex")
        and message.model_id == model_id
        and message.raw_message
        and not encode_thoughts
    ):
        return cast(anthropic_types.MessageParam, message.raw_message)
    return {
        "role": message.role,
        "content": _encode_content(message.content, encode_thoughts, provider),
    }


def _prepare_request(
    *,
    model_id: AnthropicModelId,
    messages: Sequence[Message],
    tools: Sequence[ToolSchema] | BaseToolkit | None,
    format: type[FormattableT] | Format[FormattableT] | None,
    params: Params,
    provider: Literal["anthropic", "anthropic-bedrock", "anthropic-vertex"],
) -> tuple[
    Sequence[Message],
    Format[FormattableT] | None,
    MessageCreateKwargs,
    bool,
    Sequence[UserMessage | AssistantMessage],
    str | None,
]:
    """Setup shared request state prior to message encoding."""
    kwargs: MessageCreateKwargs = MessageCreateKwargs(
        {
            "model": model_id,
            "max_tokens": DEFAULT_MAX_TOKENS,
        }
    )
    encode_thoughts = False

    with _base_utils.ensure_all_params_accessed(
        params=params, provider="anthropic", unsupported_params=["seed"]
    ) as param_accessor:
        if param_accessor.temperature is not None:
            kwargs["temperature"] = param_accessor.temperature
        if param_accessor.max_tokens is not None:
            kwargs["max_tokens"] = param_accessor.max_tokens
        if param_accessor.top_p is not None:
            kwargs["top_p"] = param_accessor.top_p
        if param_accessor.top_k is not None:
            kwargs["top_k"] = param_accessor.top_k
        if param_accessor.stop_sequences is not None:
            kwargs["stop_sequences"] = param_accessor.stop_sequences
        if param_accessor.thinking is not None:
            if param_accessor.thinking:
                budget_tokens = max(1024, kwargs["max_tokens"] // 2)
                kwargs["thinking"] = {"type": "enabled", "budget_tokens": budget_tokens}
            else:
                kwargs["thinking"] = {"type": "disabled"}
        if param_accessor.encode_thoughts_as_text:
            encode_thoughts = True

    tools = tools.tools if isinstance(tools, BaseToolkit) else tools or []
    anthropic_tools = [_convert_tool_to_tool_param(tool) for tool in tools]
    format = resolve_format(format, default_mode="tool")
    if format is not None:
        if format.mode == "strict":
            raise FormattingModeNotSupportedError(
                formatting_mode="strict", provider=provider
            )
        elif format.mode == "tool":
            format_tool_schema = _formatting_utils.create_tool_schema(format)
            anthropic_tools.append(_convert_tool_to_tool_param(format_tool_schema))
            if tools:
                kwargs["tool_choice"] = {"type": "any"}
            else:
                kwargs["tool_choice"] = {
                    "type": "tool",
                    "name": FORMAT_TOOL_NAME,
                    "disable_parallel_tool_use": True,
                }

        if format.formatting_instructions:
            messages = _base_utils.add_system_instructions(
                messages, format.formatting_instructions
            )

    if anthropic_tools:
        kwargs["tools"] = anthropic_tools

    system_message_content, remaining_messages = _base_utils.extract_system_message(
        messages
    )

    return (
        messages,
        format,
        kwargs,
        encode_thoughts,
        remaining_messages,
        system_message_content,
    )


@lru_cache(maxsize=128)
def _convert_tool_to_tool_param(tool: ToolSchema) -> anthropic_types.ToolParam:
    """Returns cached Anthropic ToolParam from Mirascope ToolSchema."""
    schema_dict = tool.parameters.model_dump(by_alias=True, exclude_none=True)
    schema_dict["type"] = "object"
    return anthropic_types.ToolParam(
        name=tool.name,
        description=tool.description,
        input_schema=schema_dict,
    )


def encode_request(
    *,
    model_id: AnthropicModelId,
    messages: Sequence[Message],
    tools: Sequence[ToolSchema] | BaseToolkit | None,
    format: type[FormattableT] | Format[FormattableT] | None,
    params: Params,
    provider: Literal["anthropic", "anthropic-bedrock", "anthropic-vertex"],
) -> tuple[Sequence[Message], Format[FormattableT] | None, MessageCreateKwargs]:
    """Returns tuple of (messages, format, kwargs) for Anthropic.messages.create."""
    (
        prepared_messages,
        format,
        kwargs,
        encode_thoughts,
        remaining_messages,
        system_message_content,
    ) = _prepare_request(
        model_id=model_id,
        messages=messages,
        tools=tools,
        format=format,
        params=params,
        provider=provider,
    )

    kwargs["messages"] = [
        _encode_message(remaining_message, model_id, encode_thoughts, provider)
        for remaining_message in remaining_messages
    ]

    if system_message_content:
        kwargs["system"] = system_message_content

    return prepared_messages, format, kwargs
