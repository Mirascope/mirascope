"""Standard Anthropic message encoding and request preparation."""

import json
from collections.abc import Sequence
from functools import lru_cache
from typing import TypedDict, cast
from typing_extensions import Required

from anthropic import Omit, types as anthropic_types

from .....content import ContentPart
from .....exceptions import FeatureNotSupportedError, FormattingModeNotSupportedError
from .....formatting import (
    Format,
    FormattableT,
    _utils as _formatting_utils,
    resolve_format,
)
from .....messages import AssistantMessage, Message, UserMessage
from .....tools import FORMAT_TOOL_NAME, AnyToolSchema, BaseToolkit
from ....base import Params, _utils as _base_utils
from ..._utils import DEFAULT_MAX_TOKENS, encode_image_mime_type, process_params
from ...model_id import AnthropicModelId, model_name

DEFAULT_FORMAT_MODE = "tool"


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


def encode_content(
    content: Sequence[ContentPart], encode_thoughts: bool
) -> str | Sequence[anthropic_types.ContentBlockParam]:
    """Convert mirascope content to Anthropic content format."""

    if len(content) == 1 and content[0].type == "text":
        if not content[0].text:
            raise FeatureNotSupportedError(
                "empty message content",
                "anthropic",
                message="Anthropic does not support empty message content.",
            )
        return content[0].text

    blocks: list[anthropic_types.ContentBlockParam] = []

    for part in content:
        if part.type == "text":
            if part.text:
                blocks.append(
                    anthropic_types.TextBlockParam(type="text", text=part.text)
                )
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
            else:  # url_image_source
                source = anthropic_types.URLImageSourceParam(
                    type="url",
                    url=part.source.url,
                )
            blocks.append(anthropic_types.ImageBlockParam(type="image", source=source))
        elif part.type == "audio":
            raise FeatureNotSupportedError(
                "audio input",
                "anthropic",
                message="Anthropic does not support audio inputs.",
            )
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
        else:
            raise NotImplementedError(f"Unsupported content type: {part.type}")

    if not blocks:
        raise FeatureNotSupportedError(
            "empty message content",
            "anthropic",
            message="Anthropic does not support empty message content.",
        )

    return blocks


def _encode_message(
    message: UserMessage | AssistantMessage,
    model_id: AnthropicModelId,
    encode_thoughts: bool,
) -> anthropic_types.MessageParam:
    """Convert user or assistant Message to Anthropic MessageParam format."""
    if (
        message.role == "assistant"
        and message.provider_id == "anthropic"
        and message.model_id == model_id
        and message.raw_message
        and not encode_thoughts
    ):
        return cast(anthropic_types.MessageParam, message.raw_message)
    return {
        "role": message.role,
        "content": encode_content(message.content, encode_thoughts),
    }


@lru_cache(maxsize=128)
def convert_tool_to_tool_param(tool: AnyToolSchema) -> anthropic_types.ToolParam:
    """Convert a single Mirascope tool to Anthropic tool format with caching."""
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
    tools: Sequence[AnyToolSchema] | BaseToolkit[AnyToolSchema] | None,
    format: type[FormattableT] | Format[FormattableT] | None,
    params: Params,
) -> tuple[Sequence[Message], Format[FormattableT] | None, MessageCreateKwargs]:
    """Prepares a request for the Anthropic messages.create method."""

    processed = process_params(params, DEFAULT_MAX_TOKENS)
    encode_thoughts = processed.pop("encode_thoughts", False)
    max_tokens = processed.pop("max_tokens", DEFAULT_MAX_TOKENS)

    kwargs: MessageCreateKwargs = MessageCreateKwargs(
        {"model": model_name(model_id), "max_tokens": max_tokens, **processed}
    )

    tools = tools.tools if isinstance(tools, BaseToolkit) else tools or []
    anthropic_tools = [convert_tool_to_tool_param(tool) for tool in tools]
    format = resolve_format(format, default_mode=DEFAULT_FORMAT_MODE)
    if format is not None:
        if format.mode == "strict":
            raise FormattingModeNotSupportedError(
                formatting_mode="strict",
                provider_id="anthropic",
                model_id=model_id,
            )
        if format.mode == "tool":
            format_tool_schema = _formatting_utils.create_tool_schema(format)
            anthropic_tools.append(convert_tool_to_tool_param(format_tool_schema))
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

    kwargs["messages"] = [
        _encode_message(remaining_message, model_id, encode_thoughts)
        for remaining_message in remaining_messages
    ]

    if system_message_content:
        kwargs["system"] = system_message_content

    return messages, format, kwargs
