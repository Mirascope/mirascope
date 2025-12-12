"""Together AI message encoding and request preparation.

Together AI provides an OpenAI-compatible Chat Completions API. This module
mirrors the OpenAI completions encode logic, but emits plain dict kwargs for
Together's SDK.
"""

from __future__ import annotations

from collections.abc import Sequence
from functools import lru_cache
from typing import Any, Literal, TypedDict, cast
from typing_extensions import Required

from ....exceptions import FeatureNotSupportedError, FormattingModeNotSupportedError
from ....formatting import (
    Format,
    FormattableT,
    _utils as _formatting_utils,
    resolve_format,
)
from ....messages import AssistantMessage, Message, UserMessage
from ....tools import FORMAT_TOOL_NAME, AnyToolSchema, BaseToolkit
from ...base import Params, _utils as _base_utils
from ..model_id import TogetherModelId, model_name


class TextContentPart(TypedDict):
    type: Literal["text"]
    text: str


class ImageUrlDetail(TypedDict):
    url: str


class ImageContentPart(TypedDict):
    type: Literal["image_url"]
    image_url: ImageUrlDetail


ContentPart = TextContentPart | ImageContentPart


class ToolCallFunction(TypedDict):
    name: str
    arguments: str


class ToolCallParam(TypedDict):
    id: str
    type: Literal["function"]
    function: ToolCallFunction


class SystemMessageParam(TypedDict):
    role: Literal["system"]
    content: str


class UserMessageParam(TypedDict, total=False):
    role: Required[Literal["user"]]
    content: Required[str | list[ContentPart]]


class ToolMessageParam(TypedDict):
    role: Literal["tool"]
    content: str
    tool_call_id: str
    name: str


class AssistantMessageParam(TypedDict, total=False):
    role: Required[Literal["assistant"]]
    content: str | list[TextContentPart] | None
    tool_calls: list[ToolCallParam]


MessageParam = (
    SystemMessageParam | UserMessageParam | ToolMessageParam | AssistantMessageParam
)


class FunctionParam(TypedDict, total=False):
    name: Required[str]
    description: str
    parameters: dict[str, Any]
    strict: bool


class ToolParam(TypedDict):
    type: Literal["function"]
    function: FunctionParam


class FunctionChoice(TypedDict):
    name: str


class ToolChoiceFunction(TypedDict):
    type: Literal["function"]
    function: FunctionChoice


ToolChoice = str | ToolChoiceFunction


class JsonSchemaDetail(TypedDict, total=False):
    name: Required[str]
    schema: Required[dict[str, Any]]
    strict: bool
    description: str


class JsonSchemaResponseFormat(TypedDict):
    type: Literal["json_schema"]
    json_schema: JsonSchemaDetail


class JsonObjectResponseFormat(TypedDict):
    type: Literal["json_object"]


ResponseFormat = JsonSchemaResponseFormat | JsonObjectResponseFormat


class ChatCompletionCreateKwargs(TypedDict, total=False):
    """Kwargs for Together chat.completions.create method.

    Types match Together SDK's sync `ChatCompletions.create` signature.
    Note: Together SDK accepts `Dict[str, Any]` so these are cast at the boundary.
    """

    model: Required[str]
    messages: Required[list[MessageParam]]
    tools: list[ToolParam]
    response_format: ResponseFormat
    tool_choice: ToolChoice
    temperature: float
    max_tokens: int
    top_p: float
    top_k: int
    seed: int
    stop: list[str]


def _encode_user_message(message: UserMessage) -> list[MessageParam]:
    """Convert Mirascope `UserMessage` to Together message dict(s)."""
    current_content: list[ContentPart] = []
    result: list[MessageParam] = []

    def flush_message_content() -> None:
        nonlocal current_content
        if current_content:
            first = current_content[0]
            if len(current_content) == 1 and first["type"] == "text":
                result.append(UserMessageParam(role="user", content=first["text"]))
            else:
                result.append(UserMessageParam(role="user", content=current_content))
            current_content = []

    for part in message.content:
        if part.type == "text":
            current_content.append({"type": "text", "text": part.text})
        elif part.type == "image":
            url = (
                part.source.url
                if part.source.type == "url_image_source"
                else f"data:{part.source.mime_type};base64,{part.source.data}"
            )
            current_content.append({"type": "image_url", "image_url": {"url": url}})
        elif part.type == "audio":
            raise FeatureNotSupportedError(
                feature="Audio inputs",
                provider_id="together",
                message="Together chat completions do not currently support audio inputs via Mirascope.",
            )
        elif part.type == "tool_output":
            flush_message_content()
            result.append(
                {
                    "role": "tool",
                    "content": str(part.value),
                    "tool_call_id": part.id,
                    "name": part.name,
                }
            )
        else:
            raise NotImplementedError(
                f"Unsupported user content part type: {part.type}"
            )
    flush_message_content()
    return result


def _encode_assistant_message(
    message: AssistantMessage, model_id: TogetherModelId, encode_thoughts: bool
) -> AssistantMessageParam:
    """Convert Mirascope `AssistantMessage` to Together assistant message dict."""
    if (
        message.provider_id == "together"
        and message.provider_model_name == model_name(model_id)
        and message.raw_message
        and not encode_thoughts
    ):
        return cast(AssistantMessageParam, message.raw_message)

    text_parts: list[TextContentPart] = []
    tool_calls: list[ToolCallParam] = []
    for part in message.content:
        if part.type == "text":
            text_parts.append({"type": "text", "text": part.text})
        elif part.type == "tool_call":
            tool_calls.append(
                {
                    "id": part.id,
                    "type": "function",
                    "function": {"name": part.name, "arguments": part.args},
                }
            )
        elif part.type == "thought":
            if encode_thoughts:
                text_parts.append(
                    {"type": "text", "text": "**Thinking:** " + part.thought}
                )
        else:
            raise NotImplementedError(f"Unsupported content type: {part.type}")

    content: str | list[TextContentPart] | None = None
    if len(text_parts) == 1:
        content = text_parts[0]["text"]
    elif text_parts:
        content = text_parts

    encoded: AssistantMessageParam = {"role": "assistant", "content": content}
    if tool_calls:
        encoded["tool_calls"] = tool_calls
    return encoded


def _encode_message(
    message: Message, model_id: TogetherModelId, encode_thoughts: bool
) -> list[MessageParam]:
    if message.role == "system":
        return [SystemMessageParam(role="system", content=message.content.text)]
    if message.role == "user":
        return _encode_user_message(message)
    if message.role == "assistant":
        return [_encode_assistant_message(message, model_id, encode_thoughts)]
    raise ValueError(f"Unsupported role: {message.role}")  # pragma: no cover


@lru_cache(maxsize=128)
def _convert_tool_to_tool_param(tool: AnyToolSchema) -> ToolParam:
    schema_dict = tool.parameters.model_dump(by_alias=True, exclude_none=True)
    schema_dict["type"] = "object"
    _base_utils.ensure_additional_properties_false(schema_dict)
    function: FunctionParam = {
        "name": tool.name,
        "description": tool.description,
        "parameters": schema_dict,
        "strict": tool.strict,
    }
    return {"type": "function", "function": function}


def encode_request(
    *,
    model_id: TogetherModelId,
    messages: Sequence[Message],
    tools: Sequence[AnyToolSchema] | BaseToolkit[AnyToolSchema] | None,
    format: type[FormattableT] | Format[FormattableT] | None,
    params: Params,
) -> tuple[Sequence[Message], Format[FormattableT] | None, ChatCompletionCreateKwargs]:
    """Prepare a request for Together `chat.completions.create`."""
    if not model_id.startswith("together/"):  # pragma: no cover
        raise ValueError(
            f"Model ID must start with 'together/' prefix, got: {model_id}"
        )

    kwargs: ChatCompletionCreateKwargs = {
        "model": model_name(model_id),
        "messages": [],
    }
    encode_thoughts = False

    with _base_utils.ensure_all_params_accessed(
        params=params, provider_id="together", unsupported_params=["thinking"]
    ) as param_accessor:
        if param_accessor.temperature is not None:
            kwargs["temperature"] = param_accessor.temperature
        if param_accessor.max_tokens is not None:
            kwargs["max_tokens"] = param_accessor.max_tokens
        if param_accessor.top_p is not None:
            kwargs["top_p"] = param_accessor.top_p
        if param_accessor.top_k is not None:
            kwargs["top_k"] = param_accessor.top_k
        if param_accessor.seed is not None:
            kwargs["seed"] = param_accessor.seed
        if param_accessor.stop_sequences is not None:
            kwargs["stop"] = param_accessor.stop_sequences
        if param_accessor.encode_thoughts_as_text is not None:
            encode_thoughts = bool(param_accessor.encode_thoughts_as_text)

    tools = tools.tools if isinstance(tools, BaseToolkit) else tools or []
    together_tools = [_convert_tool_to_tool_param(tool) for tool in tools]

    format = resolve_format(format, default_mode="tool")
    if format is not None:
        if format.mode == "strict":
            # Together AI models follow JSON structure but ignore semantic instructions
            # in schema descriptions (e.g., "rating should be 7" gets ignored).
            # Verified with Llama-4-Maverick-17B-128E-Instruct-FP8 on 2025-12-12.
            raise FeatureNotSupportedError(
                feature="strict formatting mode",
                provider_id="together",
                model_id=model_id,
            )
        elif format.mode == "tool":
            if (
                tools
            ):  # pragma: no cover - Together doesn't support format + tools reliably
                kwargs["tool_choice"] = "required"
            else:
                tool_choice: ToolChoiceFunction = {
                    "type": "function",
                    "function": {"name": FORMAT_TOOL_NAME},
                }
                kwargs["tool_choice"] = tool_choice
            format_tool_schema = _formatting_utils.create_tool_schema(format)
            together_tools.append(_convert_tool_to_tool_param(format_tool_schema))
        elif format.mode == "json":
            json_format: JsonObjectResponseFormat = {"type": "json_object"}
            kwargs["response_format"] = json_format
        else:  # pragma: no cover
            raise FormattingModeNotSupportedError(
                formatting_mode=format.mode,
                provider_id="together",
                model_id=model_id,
            )

        if format.formatting_instructions:
            messages = _base_utils.add_system_instructions(
                messages, format.formatting_instructions
            )

    if together_tools:
        kwargs["tools"] = together_tools

    encoded_messages: list[MessageParam] = []
    for message in messages:
        encoded_messages.extend(_encode_message(message, model_id, encode_thoughts))
    kwargs["messages"] = encoded_messages

    return messages, format, kwargs
