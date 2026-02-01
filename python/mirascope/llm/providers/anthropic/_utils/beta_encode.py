"""Beta Anthropic message encoding and request preparation."""

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, TypedDict, cast
from typing_extensions import Required

from anthropic import Omit
from anthropic.types.anthropic_beta_param import AnthropicBetaParam
from anthropic.types.beta import (
    BetaCacheControlEphemeralParam,
    BetaContentBlockParam,
    BetaMessageParam,
    BetaTextBlockParam,
    BetaThinkingConfigParam,
    BetaToolChoiceParam,
    BetaToolParam,
    BetaToolUnionParam,
    BetaWebSearchTool20250305Param,
)
from pydantic import BaseModel

from ....content import ContentPart
from ....exceptions import FeatureNotSupportedError
from ....formatting import (
    Format,
    FormatSpec,
    FormattableT,
    resolve_format,
)
from ....messages import AssistantMessage, Message, UserMessage
from ....tools import AnyToolSchema, BaseToolkit, ProviderTool, WebSearchTool
from ...base import _utils as _base_utils
from ..model_id import model_name
from ..model_info import MODELS_WITHOUT_STRICT_STRUCTURED_OUTPUTS
from .encode import (
    DEFAULT_MAX_TOKENS,
    FORMAT_TOOL_NAME,
    encode_content,
    process_params,
)

if TYPE_CHECKING:
    from ....models import Params

DEFAULT_FORMAT_MODE = "strict"


class BetaParseKwargs(TypedDict, total=False):
    """Kwargs for Anthropic beta.messages.parse method."""

    model: Required[str]
    max_tokens: Required[int]
    messages: Sequence[BetaMessageParam]
    system: Sequence[BetaTextBlockParam] | Omit
    tools: Sequence[BetaToolUnionParam] | Omit
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
    encode_thoughts_as_text: bool,
    add_cache_control: bool = False,
) -> str | Sequence[BetaContentBlockParam]:
    """Convert mirascope content to Beta Anthropic content format."""
    result = encode_content(content, encode_thoughts_as_text, add_cache_control)
    if isinstance(result, str):
        return result
    return cast(Sequence[BetaContentBlockParam], result)


def _beta_encode_message(
    message: UserMessage | AssistantMessage,
    model_id: str,
    encode_thoughts_as_text: bool,
    add_cache_control: bool = False,
) -> BetaMessageParam:
    """Convert user or assistant Message to Beta MessageParam format.

    Args:
        message: The message to encode
        model_id: The Anthropic model ID
        encode_thoughts_as_text: Whether to encode thought blocks as text
        add_cache_control: Whether to add cache_control to the last content block
    """
    if (
        message.role == "assistant"
        and message.provider_id == "anthropic"
        and message.model_id == model_id
        and message.raw_message
        and not encode_thoughts_as_text
        and not add_cache_control
    ):
        raw = cast(dict[str, Any], message.raw_message)
        return BetaMessageParam(
            role=raw["role"],
            content=raw["content"],
        )

    content = _beta_encode_content(
        message.content, encode_thoughts_as_text, add_cache_control
    )

    return BetaMessageParam(
        role=message.role,
        content=content,
    )


def _beta_encode_messages(
    messages: Sequence[UserMessage | AssistantMessage],
    model_id: str,
    encode_thoughts_as_text: bool,
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
            _beta_encode_message(message, model_id, encode_thoughts_as_text, add_cache)
        )
    return encoded_messages


def _beta_convert_tool_to_tool_param(
    tool: "AnyToolSchema | ProviderTool", model_supports_strict: bool
) -> BetaToolUnionParam:
    """Convert a single Mirascope tool to Beta Anthropic tool format.

    If the tool has strict=True (or None, and the model supports strict), the schema
    is modified to be compatible with Anthropic's strict structured outputs beta
    by adding additionalProperties: false to all object schemas, and strict=True
    is passed to the API.
    """
    if isinstance(tool, WebSearchTool):
        return BetaWebSearchTool20250305Param(
            type="web_search_20250305", name="web_search"
        )
    if isinstance(tool, ProviderTool):
        raise FeatureNotSupportedError(
            f"Provider tool {tool.name}", provider_id="anthropic-beta"
        )
    schema_dict = tool.parameters.model_dump(by_alias=True, exclude_none=True)
    schema_dict["type"] = "object"

    strict = model_supports_strict if tool.strict is None else tool.strict
    if strict:
        _base_utils.ensure_additional_properties_false(schema_dict)

    return BetaToolParam(
        name=tool.name,
        description=tool.description,
        input_schema=schema_dict,
        strict=strict,
    )


def beta_encode_request(
    *,
    model_id: str,
    messages: Sequence[Message],
    tools: BaseToolkit[AnyToolSchema],
    format: FormatSpec[FormattableT] | None,
    params: "Params",
) -> tuple[Sequence[Message], Format[FormattableT] | None, BetaParseKwargs]:
    """Prepares a request for the Anthropic beta.messages.parse method."""

    processed = process_params(params, DEFAULT_MAX_TOKENS)
    encode_thoughts_as_text = processed.pop("encode_thoughts_as_text", False)
    max_tokens = processed.pop("max_tokens", DEFAULT_MAX_TOKENS)

    kwargs: BetaParseKwargs = BetaParseKwargs(
        {
            "model": model_name(model_id),
            "max_tokens": max_tokens,
            "betas": ["structured-outputs-2025-11-13"],
            **processed,
        }
    )

    model_supports_strict = (
        model_name(model_id) not in MODELS_WITHOUT_STRICT_STRUCTURED_OUTPUTS
    )
    # Check for strict tools on models that don't support them
    if _base_utils.has_strict_tools(tools.tools) and not model_supports_strict:
        raise FeatureNotSupportedError(
            feature="strict tools",
            provider_id="anthropic",
            model_id=model_id,
            message="Strict tools require a model that supports structured outputs. "
            "Use a newer model like claude-sonnet-4-5 or set strict=False on your tools.",
        )

    anthropic_tools = [
        _beta_convert_tool_to_tool_param(
            tool, model_supports_strict=model_supports_strict
        )
        for tool in tools.tools
    ]
    format = resolve_format(format, default_mode=DEFAULT_FORMAT_MODE)

    if format is not None:
        if format.mode == "strict":
            if model_name(model_id) in MODELS_WITHOUT_STRICT_STRUCTURED_OUTPUTS:
                raise FeatureNotSupportedError(
                    feature=f"formatting_mode:{format.mode}",
                    provider_id="anthropic",
                    model_id=model_id,
                )
            else:
                kwargs["output_format"] = cast(type[BaseModel], format.formattable)

        if format.mode == "tool":
            format_tool_schema = format.create_tool_schema()
            anthropic_tools.append(
                _beta_convert_tool_to_tool_param(
                    format_tool_schema, model_supports_strict=model_supports_strict
                )
            )
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
        last_tool["cache_control"] = BetaCacheControlEphemeralParam(type="ephemeral")
        kwargs["tools"] = anthropic_tools

    system_message_content, remaining_messages = _base_utils.extract_system_message(
        messages
    )

    kwargs["messages"] = _beta_encode_messages(
        remaining_messages, model_id, encode_thoughts_as_text
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
