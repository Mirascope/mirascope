"""Shared Anthropic encoding utilities."""

from __future__ import annotations

import json
from collections.abc import Sequence
from functools import lru_cache
from typing import TYPE_CHECKING, Any, Literal, TypedDict, cast
from typing_extensions import Required

from anthropic import Omit, types as anthropic_types

from ....content import ContentPart, ImageMimeType
from ....exceptions import FeatureNotSupportedError
from ....formatting import (
    Format,
    FormatSpec,
    FormattableT,
    resolve_format,
)
from ....messages import AssistantMessage, Message, UserMessage
from ....tools import (
    FORMAT_TOOL_NAME,
    AnyToolSchema,
    BaseToolkit,
    ProviderTool,
    WebSearchTool,
)
from ...base import _utils as _base_utils
from ..model_id import AnthropicModelId, model_name

if TYPE_CHECKING:
    from ....models import Params, ThinkingLevel

DEFAULT_MAX_TOKENS = 16000
# TODO: Change DEFAULT_FORMAT_MODE to strict when strict is no longer a beta feature.
DEFAULT_FORMAT_MODE = "tool"

# Thinking level to a float multiplier % of max tokens
THINKING_LEVEL_TO_BUDGET_MULTIPLIER: dict[ThinkingLevel, float] = {
    "minimal": 0,  # Will become 1024 (actual minimal value)
    "low": 0.2,
    "medium": 0.4,
    "high": 0.6,
    "max": 0.8,
}

AnthropicImageMimeType = Literal["image/jpeg", "image/png", "image/gif", "image/webp"]


def encode_image_mime_type(mime_type: ImageMimeType) -> AnthropicImageMimeType:
    """Convert an ImageMimeType into anthropic supported mime type."""
    if mime_type in ("image/jpeg", "image/png", "image/gif", "image/webp"):
        return mime_type
    raise FeatureNotSupportedError(
        feature=f"Image with mime_type: {mime_type}", provider_id="anthropic"
    )  # pragma: no cover


def compute_thinking_budget(
    level: ThinkingLevel,
    max_tokens: int,
) -> int:
    """Compute Anthropic token budget from ThinkingConfig level.

    Args:
        level: The thinking level from ThinkingConfig
        max_tokens: The max_tokens value for the request

    Returns:
        Token budget for thinking (0 to disable, positive for budget)
    """

    if level == "none":
        return 0
    elif level == "default":
        return -1  # Do not set thinking, leave to provider default

    multiplier: float = THINKING_LEVEL_TO_BUDGET_MULTIPLIER.get(level, 0.4)
    budget = int(multiplier * max_tokens)
    return max(1024, budget)  # Always return at least 1024, minimum allowed budget


class ProcessedParams(TypedDict, total=False):
    """Common parameters processed from Params."""

    temperature: float
    max_tokens: int
    top_p: float
    top_k: int
    stop_sequences: list[str]
    thinking: dict[str, Any]
    encode_thoughts_as_text: bool


def process_params(params: Params, default_max_tokens: int) -> ProcessedParams:
    """Process common Anthropic parameters from Params.

    Returns a dict with processed parameters that can be merged into kwargs.
    """
    result: ProcessedParams = {
        "max_tokens": default_max_tokens,
        "encode_thoughts_as_text": False,
    }

    with _base_utils.ensure_all_params_accessed(
        params=params, provider_id="anthropic", unsupported_params=["seed"]
    ) as param_accessor:
        if param_accessor.temperature is not None:
            result["temperature"] = param_accessor.temperature
        if param_accessor.max_tokens is not None:
            result["max_tokens"] = param_accessor.max_tokens
        if param_accessor.top_p is not None:
            result["top_p"] = param_accessor.top_p
        if param_accessor.top_k is not None:
            result["top_k"] = param_accessor.top_k
        if param_accessor.stop_sequences is not None:
            result["stop_sequences"] = param_accessor.stop_sequences
        if param_accessor.thinking is not None:
            thinking_config = param_accessor.thinking
            level = thinking_config.get("level")

            # Compute token budget from level
            budget_tokens = compute_thinking_budget(level, result["max_tokens"])
            if budget_tokens == 0:
                result["thinking"] = {"type": "disabled"}
            elif budget_tokens > 0:
                result["thinking"] = {"type": "enabled", "budget_tokens": budget_tokens}
            else:
                # budget is -1, do not set thinking at all.
                pass

            # Handle encode_thoughts_as_text from ThinkingConfig
            if thinking_config.get("encode_thoughts_as_text"):
                result["encode_thoughts_as_text"] = True

    return result


class MessageCreateKwargs(TypedDict, total=False):
    """Kwargs for Anthropic Message.create method."""

    model: Required[str]
    max_tokens: Required[int]
    messages: Sequence[anthropic_types.MessageParam]
    system: Sequence[anthropic_types.TextBlockParam] | Omit
    tools: Sequence[anthropic_types.ToolUnionParam] | Omit
    tool_choice: anthropic_types.ToolChoiceParam | Omit
    temperature: float | Omit
    top_p: float | Omit
    top_k: int | Omit
    stop_sequences: list[str] | Omit
    thinking: anthropic_types.ThinkingConfigParam | Omit


def encode_content(
    content: Sequence[ContentPart],
    encode_thoughts: bool,
    add_cache_control: bool,
) -> str | Sequence[anthropic_types.ContentBlockParam]:
    """Convert mirascope content to Anthropic content format."""

    if len(content) == 1 and content[0].type == "text":
        if not content[0].text:
            raise FeatureNotSupportedError(
                "empty message content",
                "anthropic",
                message="Anthropic does not support empty message content.",
            )
        if add_cache_control:
            return [
                anthropic_types.TextBlockParam(
                    type="text",
                    text=content[0].text,
                    cache_control={"type": "ephemeral"},
                )
            ]
        return content[0].text

    blocks: list[anthropic_types.ContentBlockParam] = []

    # Find the last cacheable content part (text, image, tool_result, or tool_call)
    last_cacheable_index = -1
    if add_cache_control:
        for i in range(len(content) - 1, -1, -1):
            part = content[i]
            if part.type in ("text", "image", "tool_output", "tool_call"):
                if part.type == "text" and not part.text:  # pragma: no cover
                    continue  # Skip empty text
                last_cacheable_index = i
                break

    for i, part in enumerate(content):
        should_add_cache = add_cache_control and i == last_cacheable_index

        if part.type == "text":
            if part.text:
                blocks.append(
                    anthropic_types.TextBlockParam(
                        type="text",
                        text=part.text,
                        cache_control={"type": "ephemeral"}
                        if should_add_cache
                        else None,
                    )
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
            blocks.append(
                anthropic_types.ImageBlockParam(
                    type="image",
                    source=source,
                    cache_control={"type": "ephemeral"} if should_add_cache else None,
                )
            )
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
                    content=str(part.result),
                    cache_control={"type": "ephemeral"} if should_add_cache else None,
                )
            )
        elif part.type == "tool_call":
            blocks.append(
                anthropic_types.ToolUseBlockParam(
                    type="tool_use",
                    id=part.id,
                    name=part.name,
                    input=json.loads(part.args),
                    cache_control={"type": "ephemeral"} if should_add_cache else None,
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
    add_cache_control: bool = False,
) -> anthropic_types.MessageParam:
    """Convert user or assistant Message to Anthropic MessageParam format.

    Args:
        message: The message to encode
        model_id: The Anthropic model ID
        encode_thoughts: Whether to encode thought blocks as text
        add_cache_control: Whether to add cache_control to the last content block
    """
    if (
        message.role == "assistant"
        and message.provider_id == "anthropic"
        and message.model_id == model_id
        and message.raw_message
        and not encode_thoughts
        and not add_cache_control
    ):
        return cast(anthropic_types.MessageParam, message.raw_message)

    content = encode_content(message.content, encode_thoughts, add_cache_control)

    return {
        "role": message.role,
        "content": content,
    }


def _encode_messages(
    messages: Sequence[UserMessage | AssistantMessage],
    model_id: AnthropicModelId,
    encode_thoughts_as_text: bool,
) -> Sequence[anthropic_types.MessageParam]:
    """Encode messages and add cache control for multi-turn conversations.

    If the conversation contains assistant messages (indicating multi-turn),
    adds cache_control to the last content block of the last message.
    """
    # Detect multi-turn conversations by checking for assistant messages
    has_assistant_message = any(msg.role == "assistant" for msg in messages)

    # Encode messages, adding cache_control to the last message if multi-turn
    encoded_messages: list[anthropic_types.MessageParam] = []
    for i, message in enumerate(messages):
        is_last = i == len(messages) - 1
        add_cache = has_assistant_message and is_last
        encoded_messages.append(
            _encode_message(message, model_id, encode_thoughts_as_text, add_cache)
        )
    return encoded_messages


@lru_cache(maxsize=128)
def convert_tool_to_tool_param(
    tool: AnyToolSchema | ProviderTool,
) -> anthropic_types.ToolUnionParam:
    """Convert a single Mirascope tool to Anthropic tool format with caching."""
    if isinstance(tool, WebSearchTool):
        return anthropic_types.WebSearchTool20250305Param(
            type="web_search_20250305", name="web_search"
        )
    if isinstance(tool, ProviderTool):
        raise FeatureNotSupportedError(
            f"Provider tool {tool.name}", provider_id="anthropic"
        )
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
    tools: BaseToolkit[AnyToolSchema],
    format: FormatSpec[FormattableT] | None,
    params: Params,
) -> tuple[Sequence[Message], Format[FormattableT] | None, MessageCreateKwargs]:
    """Prepares a request for the Anthropic messages.create method."""

    processed = process_params(params, DEFAULT_MAX_TOKENS)
    encode_thoughts_as_text = processed.pop("encode_thoughts_as_text", False)
    max_tokens = processed.pop("max_tokens", DEFAULT_MAX_TOKENS)

    kwargs: MessageCreateKwargs = MessageCreateKwargs(
        {"model": model_name(model_id), "max_tokens": max_tokens, **processed}
    )

    # Check for strict tools - the non-beta API doesn't support them
    if _base_utils.has_strict_tools(tools.tools):
        raise FeatureNotSupportedError(
            feature="strict tools",
            provider_id="anthropic",
            model_id=model_id,
            message="Anthropic provider does not support strict tools. Try the beta provider.",
        )

    anthropic_tools = [convert_tool_to_tool_param(tool) for tool in tools.tools]
    format = resolve_format(format, default_mode=DEFAULT_FORMAT_MODE)
    if format is not None:
        if format.mode == "strict":
            raise FeatureNotSupportedError(
                feature="formatting_mode:strict",
                provider_id="anthropic",
                model_id=model_id,
            )
        if format.mode == "tool":
            format_tool_schema = format.create_tool_schema()
            anthropic_tools.append(convert_tool_to_tool_param(format_tool_schema))
            if tools.tools:
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
        # Add cache control to the last tool for prompt caching
        last_tool = anthropic_tools[-1]
        last_tool["cache_control"] = anthropic_types.CacheControlEphemeralParam(
            type="ephemeral"
        )
        kwargs["tools"] = anthropic_tools

    system_message_content, remaining_messages = _base_utils.extract_system_message(
        messages
    )

    kwargs["messages"] = _encode_messages(
        remaining_messages, model_id, encode_thoughts_as_text
    )

    if system_message_content:
        kwargs["system"] = [
            anthropic_types.TextBlockParam(
                type="text",
                text=system_message_content,
                cache_control={"type": "ephemeral"},
            )
        ]

    return messages, format, kwargs
