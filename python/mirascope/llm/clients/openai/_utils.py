"""OpenAI message types and conversion utilities."""

import logging
from collections.abc import Sequence
from functools import lru_cache
from typing import Literal

from openai import NotGiven, Stream
from openai.types import chat as openai_types, shared_params as shared_openai_types
from openai.types.shared_params.response_format_json_schema import JSONSchema

from ...content import (
    AssistantContentPart,
    FinishReasonChunk,
    Text,
    TextChunk,
    TextEndChunk,
    TextStartChunk,
    ToolCall,
    ToolCallChunk,
    ToolCallEndChunk,
    ToolCallStartChunk,
)
from ...formatting import (
    FormatInfo,
    FormatT,
    FormattingMode,
    _utils as _formatting_utils,
)
from ...messages import AssistantMessage, Message, UserMessage
from ...responses import (
    ChunkIterator,
    FinishReason,
    RawChunk,
)
from ...tools import (
    FORMAT_TOOL_NAME,
    Tool,
)
from ..base import _utils as _base_utils
from .models import OpenAIModel

OPENAI_FINISH_REASON_MAP = {
    "stop": FinishReason.END_TURN,
    "length": FinishReason.MAX_TOKENS,
    "content_filter": FinishReason.REFUSAL,
    "tool_calls": FinishReason.TOOL_USE,
    "function_call": FinishReason.TOOL_USE,
}


def _ensure_additional_properties_false(obj: object) -> None:
    """Recursively adds additionalProperties = False to a schema, required by OpenAI API."""
    if isinstance(obj, dict):
        if obj.get("type") == "object" and "additionalProperties" not in obj:
            obj["additionalProperties"] = False
        for value in obj.values():
            _ensure_additional_properties_false(value)
    elif isinstance(obj, list):
        for item in obj:
            _ensure_additional_properties_false(item)


def _encode_user_message(
    message: UserMessage,
) -> list[openai_types.ChatCompletionMessageParam]:
    """Convert Mirascope `UserMessage` to a list of OpenAI `ChatCompletionMessageParam`."""

    message_params: list[openai_types.ChatCompletionMessageParam] = []
    for part in message.content:
        if part.type == "text":
            message_params.append(
                openai_types.ChatCompletionUserMessageParam(
                    role="user",
                    content=part.text,
                )
            )
        elif part.type == "tool_output":
            message_params.append(
                openai_types.ChatCompletionToolMessageParam(
                    role="tool",
                    content=str(part.value),
                    tool_call_id=part.id,
                )
            )
        else:
            raise NotImplementedError

    return message_params


def _encode_assistant_message(
    message: AssistantMessage,
) -> openai_types.ChatCompletionAssistantMessageParam:
    """Convert Mirascope `AssistantMessage` to OpenAI `ChatCompletionAssistantMessageParam`."""

    text_params: list[openai_types.ChatCompletionContentPartTextParam] = []
    tool_call_params: list[openai_types.ChatCompletionMessageToolCallParam] = []
    for part in message.content:
        if part.type == "text":
            text_params.append(
                openai_types.ChatCompletionContentPartTextParam(
                    text=part.text, type="text"
                )
            )
        elif part.type == "tool_call":
            tool_call_params.append(
                openai_types.ChatCompletionMessageToolCallParam(
                    id=part.id,
                    type="function",
                    function={"name": part.name, "arguments": part.args},
                )
            )
        else:
            raise NotImplementedError

    content: str | list[openai_types.ChatCompletionContentPartTextParam] | None = None
    if len(text_params) == 1:
        content = text_params[0]["text"]
    elif text_params:
        content = text_params

    message_params = {
        "role": "assistant",
        "content": content,
    }
    if tool_call_params:
        message_params["tool_calls"] = tool_call_params

    return openai_types.ChatCompletionAssistantMessageParam(**message_params)


def _encode_message(message: Message) -> list[openai_types.ChatCompletionMessageParam]:
    """Convert a Mirascope `Message` to OpenAI `ChatCompletionMessageParam` format.

    Args:
        message: A Mirascope message (system, user, or assistant)

    Returns:
        A list of OpenAI `ChatCompletionMessageParam` (may be multiple for tool outputs)
    """
    if message.role == "system":
        return [
            openai_types.ChatCompletionSystemMessageParam(
                role="system", content=message.content.text
            )
        ]
    elif message.role == "user":
        return _encode_user_message(message)
    elif message.role == "assistant":
        return [_encode_assistant_message(message)]
    else:
        raise ValueError(f"Unsupported role: {message.role}")  # pragma: no cover


@lru_cache(maxsize=128)
def _convert_tool_to_tool_param(tool: Tool) -> openai_types.ChatCompletionToolParam:
    """Convert a single Mirascope `Tool` to OpenAI ChatCompletionToolParam with caching."""
    schema_dict = tool.parameters.model_dump(by_alias=True, exclude_none=True)
    schema_dict["type"] = "object"
    return openai_types.ChatCompletionToolParam(
        type="function",
        function={
            "name": tool.name,
            "description": tool.description,
            "parameters": schema_dict,
            "strict": tool.strict,
        },
    )


def _get_effective_format_mode(
    format: FormatInfo, model: OpenAIModel
) -> FormattingMode:
    if model in MODELS_WITHOUT_JSON_SCHEMA_SUPPORT:
        if format.mode == "strict-or-tool":
            logging.info(
                "Model %s does not support strict formatting; falling back to tool",
                model,
            )
            return "tool"
        elif format.mode == "strict-or-json":
            logging.info(
                "Model %s does not support strict formatting; falling back to json",
                model,
            )
            return "json"
        return format.mode
    else:
        if format.mode in ("strict-or-tool", "strict-or-json"):
            return "strict"
        return format.mode


def prepare_openai_request(
    *,
    model: OpenAIModel,
    messages: Sequence[Message],
    tools: Sequence[Tool] | None = None,
    format: type[FormatT] | None = None,
) -> tuple[
    Sequence[Message],
    Sequence[openai_types.ChatCompletionMessageParam],
    Sequence[openai_types.ChatCompletionToolParam] | NotGiven,
    shared_openai_types.ResponseFormatJSONObject
    | shared_openai_types.ResponseFormatJSONSchema
    | NotGiven,
]:
    """Prepare OpenAI API request parameters.

    Args:
        model: The OpenAI model string. Used for model-specific behavior around whether
          strict structured outputs are supported.
        messages: A sequence of Mirascope `Message`s.
        tools: A sequence of Mirascope tools (or None).
        format: A format type (or None).

    Returns:
        A tuple containing:
            - A sequence of Mirascope `Message`s, which may include modifications to the
              system message (e.g. with instructions for JSON mode formatting).
            - A sequence of `ChatCompletionMessageParam` representing encoded message content.
            - A sequence of `ChatCompletionToolParam`, or `NotGiven`. This includes encoded tools,
              and potentially a response format tool.
            - A `ResponseFormat` specifier if needed and supported, or else `NotGiven`
    """
    openai_tools: list[openai_types.ChatCompletionToolParam] | NotGiven = (
        [_convert_tool_to_tool_param(tool) for tool in tools] if tools else []
    )

    additional_system_instructions = []
    response_format: (
        shared_openai_types.ResponseFormatJSONObject
        | shared_openai_types.ResponseFormatJSONSchema
        | NotGiven
    ) = NotGiven()

    if format:
        format_info = _formatting_utils.ensure_formattable(format)
        formatting_mode = _get_effective_format_mode(format_info, model)
        if formatting_mode == "strict":
            response_format = create_strict_response_format(format_info)
        elif formatting_mode == "tool":
            additional_system_instructions.append(
                f"When you are ready to respond to the user, call the {FORMAT_TOOL_NAME} tool to output a structured response."
            )
            additional_system_instructions.append(
                "Do NOT output any text in addition to the tool call."
            )
            openai_tools.append(create_format_tool_param(format_info))
        elif formatting_mode == "json":
            additional_system_instructions.append(
                _base_utils.create_json_mode_instructions(format_info)
            )
            if model in MODELS_WITHOUT_JSON_OBJECT_SUPPORT:
                additional_system_instructions.append(
                    "Respond ONLY with valid JSON, and no other text."
                )
            else:
                response_format = {"type": "json_object"}

        if format_info.formatting_instructions:
            additional_system_instructions.append(format_info.formatting_instructions)

    if not openai_tools:
        openai_tools = NotGiven()

    if additional_system_instructions:
        messages = _base_utils.add_system_instructions(
            messages, additional_system_instructions
        )

    encoded_messages: list[openai_types.ChatCompletionMessageParam] = []
    for message in messages:
        encoded_messages.extend(_encode_message(message))

    return messages, encoded_messages, openai_tools, response_format


def decode_response(
    response: openai_types.ChatCompletion,
) -> tuple[AssistantMessage, FinishReason]:
    """Convert OpenAI ChatCompletion to mirascope AssistantMessage."""
    choice = response.choices[0]
    message = choice.message

    parts: list[AssistantContentPart] = []
    found_format_tool_call = False
    if message.content:
        parts.append(Text(text=message.content))
    if message.tool_calls:
        for tool_call in message.tool_calls:
            if tool_call.type == "custom":
                # This should never happen, because we never create "custom" tools
                # https://platform.openai.com/docs/guides/function-calling#custom-tools
                raise NotImplementedError("OpenAI custom tools are not supported.")
            if tool_call.function.name == FORMAT_TOOL_NAME:
                parts.append(Text(text=tool_call.function.arguments))
                found_format_tool_call = True
            else:
                parts.append(
                    ToolCall(
                        id=tool_call.id,
                        name=tool_call.function.name,
                        args=tool_call.function.arguments,
                    )
                )

    finish_reason = OPENAI_FINISH_REASON_MAP.get(
        choice.finish_reason, FinishReason.UNKNOWN
    )
    if found_format_tool_call and finish_reason == FinishReason.TOOL_USE:
        finish_reason = FinishReason.END_TURN

    return AssistantMessage(content=parts), finish_reason


def convert_openai_stream_to_chunk_iterator(
    openai_stream: Stream[openai_types.ChatCompletionChunk],
) -> ChunkIterator:
    """Returns a ChunkIterator converted from an OpenAI Stream[ChatCompletionChunk]"""
    current_content_type: Literal["text", "tool_call"] | None = None
    current_tool_index: int | None = None

    # TODO: Consider moving this logic into the Response classes to avoid per-client duplication.
    current_tool_is_format_tool = False
    found_format_tool = False

    for chunk in openai_stream:
        yield RawChunk(raw=chunk)

        choice = chunk.choices[0] if chunk.choices else None
        if not choice:
            continue  # pragma: no cover

        delta = choice.delta

        if delta.content is not None:
            if current_content_type is None:
                yield TextStartChunk()
                current_content_type = "text"
            elif current_content_type == "tool_call":
                raise RuntimeError(
                    "received text delta inside tool call"
                )  # pragma: no cover
            elif current_content_type != "text":
                raise NotImplementedError

            yield TextChunk(delta=delta.content)

        if delta.tool_calls:
            if current_content_type == "text":
                # In testing, I can't get OpenAI to emit text and tool calls in the same chunk
                # But we handle this defensively.
                yield TextEndChunk()  # pragma: no cover
            elif current_content_type and current_content_type != "tool_call":
                raise RuntimeError(
                    f"Unexpected current_content_type: {current_content_type}"
                )  # pragma: no cover
            current_content_type = "tool_call"

            for tool_call_delta in delta.tool_calls:
                index = tool_call_delta.index

                if current_tool_index is not None and current_tool_index > index:
                    raise RuntimeError(
                        f"Received tool data for already-finished tool at index {index}"
                    )  # pragma: no cover

                if current_tool_index is not None and current_tool_index < index:
                    if current_tool_is_format_tool:
                        yield TextEndChunk()  # pragma: no cover
                        current_tool_is_format_tool = False  # pragma: no cover
                    else:
                        yield ToolCallEndChunk()

                    current_tool_index = None

                if current_tool_index is None:
                    if not tool_call_delta.function or not (
                        name := tool_call_delta.function.name
                    ):
                        raise RuntimeError(
                            f"Missing name for tool call at index {index}"
                        )  # pragma: no cover

                    current_tool_index = index
                    if name == FORMAT_TOOL_NAME:
                        current_tool_is_format_tool = True
                        found_format_tool = True
                    if not (tool_id := tool_call_delta.id):
                        raise RuntimeError(
                            f"Missing id for tool call at index {index}"
                        )  # pragma: no cover

                    if current_tool_is_format_tool:
                        yield TextStartChunk()
                    else:
                        yield ToolCallStartChunk(
                            id=tool_id,
                            name=name,
                        )

                if tool_call_delta.function and tool_call_delta.function.arguments:
                    if current_tool_is_format_tool:
                        yield TextChunk(delta=tool_call_delta.function.arguments)
                    else:
                        yield ToolCallChunk(delta=tool_call_delta.function.arguments)

        if choice.finish_reason:
            if current_content_type == "text" or current_tool_is_format_tool:
                yield TextEndChunk()
            elif current_content_type == "tool_call":
                yield ToolCallEndChunk()

            else:
                raise NotImplementedError

            finish_reason = OPENAI_FINISH_REASON_MAP.get(
                choice.finish_reason, FinishReason.UNKNOWN
            )
            if found_format_tool and finish_reason == FinishReason.TOOL_USE:
                finish_reason = FinishReason.END_TURN
            yield FinishReasonChunk(finish_reason=finish_reason)


def create_strict_response_format(
    format_info: FormatInfo,
) -> shared_openai_types.ResponseFormatJSONSchema:
    """Create OpenAI strict response format from a Mirascope Format.

    Args:
        format_info: The `Format` instance containing schema and metadata

    Returns:
        Dictionary containing OpenAI response_format specification
    """
    schema = format_info.schema.copy()

    _ensure_additional_properties_false(schema)

    json_schema = JSONSchema(
        name=format_info.name,
        schema=schema,
        strict=True,
    )
    if format_info.description:
        json_schema["description"] = format_info.description

    return shared_openai_types.ResponseFormatJSONSchema(
        type="json_schema", json_schema=json_schema
    )


def create_format_tool_param(
    format_info: FormatInfo,
) -> openai_types.ChatCompletionToolParam:
    """Create OpenAI `ChatCompletionToolParam` for format parsing from a Mirascope `FormatInfo`.

    Args:
        format_info: The `FormatInfo` instance containing schema and metadata

    Returns:
        OpenAI ChatCompletionToolParam for the format tool
    """
    schema_dict = format_info.schema.copy()
    schema_dict["type"] = "object"

    _ensure_additional_properties_false(schema_dict)

    description = f"Use this tool to extract data in {format_info.name} format for a final response."
    if format_info.description:
        description += "\n" + format_info.description

    return openai_types.ChatCompletionToolParam(
        type="function",
        function={
            "name": FORMAT_TOOL_NAME,
            "description": description,
            "parameters": schema_dict,
            "strict": True,
        },
    )


MODELS_WITHOUT_JSON_SCHEMA_SUPPORT = {
    "chatgpt-4o-latest",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-0125",
    "gpt-3.5-turbo-1106",
    "gpt-3.5-turbo-16k",
    "gpt-4",
    "gpt-4-0125-preview",
    "gpt-4-0613",
    "gpt-4-1106-preview",
    "gpt-4-turbo",
    "gpt-4-turbo-2024-04-09",
    "gpt-4-turbo-preview",
    "gpt-4o-2024-05-13",
    "gpt-4o-audio-preview",
    "gpt-4o-audio-preview-2024-10-01",
    "gpt-4o-audio-preview-2024-12-17",
    "gpt-4o-audio-preview-2025-06-03",
    "gpt-4o-mini-audio-preview",
    "gpt-4o-mini-audio-preview-2024-12-17",
    "gpt-5-chat-latest",
    "o1-mini",
    "o1-mini-2024-09-12",
}
MODELS_WITHOUT_JSON_OBJECT_SUPPORT = {
    "gpt-4",
    "gpt-4-0613",
    "gpt-4o-audio-preview",
    "gpt-4o-audio-preview-2024-10-01",
    "gpt-4o-audio-preview-2024-12-17",
    "gpt-4o-audio-preview-2025-06-03",
    "gpt-4o-mini-audio-preview",
    "gpt-4o-mini-audio-preview-2024-12-17",
    "gpt-4o-mini-search-preview",
    "gpt-4o-mini-search-preview-2025-03-11",
    "gpt-4o-search-preview",
    "gpt-4o-search-preview-2025-03-11",
    "o1-mini",
    "o1-mini-2024-09-12",
}
