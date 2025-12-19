"""Beta Anthropic message encoding and request preparation."""

from collections.abc import Sequence
from typing import Any, TypedDict, cast
from typing_extensions import Required

from anthropic import Omit
from anthropic.types.anthropic_beta_param import AnthropicBetaParam
from anthropic.types.beta import (
    BetaContentBlockParam,
    BetaMessageParam,
    BetaTextBlockParam,
    BetaThinkingConfigParam,
    BetaToolChoiceParam,
    BetaToolParam,
)
from pydantic import BaseModel

from ....content import ContentPart
from ....exceptions import FormattingModeNotSupportedError
from ....formatting import (
    Format,
    FormattableT,
    _utils as _formatting_utils,
    resolve_format,
)
from ....messages import AssistantMessage, Message, UserMessage
from ....tools import AnyToolSchema, BaseToolkit
from ...base import Params, _utils as _base_utils
from ..model_id import model_name
from ..model_info import MODELS_WITHOUT_STRICT_STRUCTURED_OUTPUTS
from .encode import (
    DEFAULT_MAX_TOKENS,
    FORMAT_TOOL_NAME,
    convert_tool_to_tool_param,
    encode_content,
    process_params,
)

DEFAULT_FORMAT_MODE = "strict"


class BetaParseKwargs(TypedDict, total=False):
    """Kwargs for Anthropic beta.messages.parse method."""

    model: Required[str]
    max_tokens: Required[int]
    messages: Sequence[BetaMessageParam]
    system: Sequence[BetaTextBlockParam] | Omit
    tools: Sequence[BetaToolParam] | Omit
    tool_choice: BetaToolChoiceParam | Omit
    temperature: float | Omit
    top_p: float | Omit
    top_k: int | Omit
    stop_sequences: list[str] | Omit
    thinking: BetaThinkingConfigParam | Omit
    betas: list[AnthropicBetaParam]
    output_format: type[BaseModel]


def _beta_encode_content(
    content: Sequence[ContentPart],
    encode_thoughts: bool,
    add_cache_control: bool = False,
) -> str | Sequence[BetaContentBlockParam]:
    """Convert mirascope content to Beta Anthropic content format."""
    result = encode_content(content, encode_thoughts, add_cache_control)
    if isinstance(result, str):
        return result
    return cast(Sequence[BetaContentBlockParam], result)


def _beta_encode_message(
    message: UserMessage | AssistantMessage,
    model_id: str,
    encode_thoughts: bool,
    add_cache_control: bool = False,
) -> BetaMessageParam:
    """Convert user or assistant Message to Beta MessageParam format.

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
        raw = cast(dict[str, Any], message.raw_message)
        return BetaMessageParam(
            role=raw["role"],
            content=raw["content"],
        )

    content = _beta_encode_content(message.content, encode_thoughts, add_cache_control)

    return BetaMessageParam(
        role=message.role,
        content=content,
    )


def _beta_encode_messages(
    messages: Sequence[UserMessage | AssistantMessage],
    model_id: str,
    encode_thoughts: bool,
) -> Sequence[BetaMessageParam]:
    """Encode messages and add cache control for multi-turn conversations.

    If the conversation contains assistant messages (indicating multi-turn),
    adds cache_control to the last content block of the last message.
    """
    # Detect multi-turn conversations by checking for assistant messages
    has_assistant_message = any(msg.role == "assistant" for msg in messages)

    # Encode messages, adding cache_control to the last message if multi-turn
    encoded_messages: list[BetaMessageParam] = []
    for i, message in enumerate(messages):
        is_last = i == len(messages) - 1
        add_cache = has_assistant_message and is_last
        encoded_messages.append(
            _beta_encode_message(message, model_id, encode_thoughts, add_cache)
        )
    return encoded_messages


def _beta_convert_tool_to_tool_param(tool: AnyToolSchema) -> BetaToolParam:
    """Convert a single Mirascope tool to Beta Anthropic tool format."""
    return cast(BetaToolParam, convert_tool_to_tool_param(tool))


def beta_encode_request(
    *,
    model_id: str,
    messages: Sequence[Message],
    tools: Sequence[AnyToolSchema] | BaseToolkit[AnyToolSchema] | None,
    format: type[FormattableT] | Format[FormattableT] | None,
    params: Params,
) -> tuple[Sequence[Message], Format[FormattableT] | None, BetaParseKwargs]:
    """Prepares a request for the Anthropic beta.messages.parse method."""

    processed = process_params(params, DEFAULT_MAX_TOKENS)
    encode_thoughts = processed.pop("encode_thoughts", False)
    max_tokens = processed.pop("max_tokens", DEFAULT_MAX_TOKENS)

    kwargs: BetaParseKwargs = BetaParseKwargs(
        {
            "model": model_name(model_id),
            "max_tokens": max_tokens,
            "betas": ["structured-outputs-2025-11-13"],
            **processed,
        }
    )

    tools = tools.tools if isinstance(tools, BaseToolkit) else tools or []
    anthropic_tools = [_beta_convert_tool_to_tool_param(tool) for tool in tools]
    format = resolve_format(format, default_mode=DEFAULT_FORMAT_MODE)

    if format is not None:
        if format.mode == "strict":
            if model_name(model_id) in MODELS_WITHOUT_STRICT_STRUCTURED_OUTPUTS:
                raise FormattingModeNotSupportedError(
                    formatting_mode=format.mode,
                    provider_id="anthropic",
                    model_id=model_id,
                )
            else:
                kwargs["output_format"] = cast(type[BaseModel], format.formattable)

        if format.mode == "tool":
            format_tool_schema = _formatting_utils.create_tool_schema(format)
            anthropic_tools.append(_beta_convert_tool_to_tool_param(format_tool_schema))
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
        # Add cache control to the last tool for prompt caching
        last_tool = anthropic_tools[-1]
        last_tool["cache_control"] = {"type": "ephemeral"}
        kwargs["tools"] = anthropic_tools

    system_message_content, remaining_messages = _base_utils.extract_system_message(
        messages
    )

    kwargs["messages"] = _beta_encode_messages(
        remaining_messages, model_id, encode_thoughts
    )

    if system_message_content:
        kwargs["system"] = [
            BetaTextBlockParam(
                type="text",
                text=system_message_content,
                cache_control={"type": "ephemeral"},
            )
        ]

    return messages, format, kwargs
