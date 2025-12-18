"""OpenAI completions message encoding and request preparation."""

from collections.abc import Sequence
from functools import lru_cache
from typing import TypedDict, cast

from openai import Omit
from openai.types import chat as openai_types, shared_params as shared_openai_types
from openai.types.shared_params.response_format_json_schema import JSONSchema

from .....exceptions import (
    FeatureNotSupportedError,
    FormattingModeNotSupportedError,
)
from .....formatting import (
    Format,
    FormattableT,
    _utils as _formatting_utils,
    resolve_format,
)
from .....messages import AssistantMessage, Message, UserMessage
from .....tools import FORMAT_TOOL_NAME, AnyToolSchema, BaseToolkit
from ....base import Params, _utils as _base_utils
from ...model_id import OpenAIModelId, model_name
from ...model_info import (
    MODELS_WITHOUT_AUDIO_SUPPORT,
    MODELS_WITHOUT_JSON_OBJECT_SUPPORT,
    MODELS_WITHOUT_JSON_SCHEMA_SUPPORT,
)


class ChatCompletionCreateKwargs(TypedDict, total=False):
    """Kwargs for OpenAI ChatCompletion.create method."""

    model: str
    messages: Sequence[openai_types.ChatCompletionMessageParam]
    tools: Sequence[openai_types.ChatCompletionToolParam] | Omit
    response_format: (
        shared_openai_types.ResponseFormatJSONObject
        | shared_openai_types.ResponseFormatJSONSchema
        | Omit
    )
    tool_choice: openai_types.ChatCompletionToolChoiceOptionParam | Omit
    parallel_tool_calls: bool | Omit
    temperature: float | Omit
    max_tokens: int | Omit
    top_p: float | Omit
    seed: int | Omit
    stop: str | list[str] | Omit
    reasoning_effort: shared_openai_types.ReasoningEffort | Omit


def _encode_user_message(
    message: UserMessage,
    model_id: OpenAIModelId,
) -> list[openai_types.ChatCompletionMessageParam]:
    """Convert Mirascope `UserMessage` to a list of OpenAI `ChatCompletionMessageParam`.

    Multiple text content parts are combined into a single user message.
    Tool outputs become separate tool messages.
    """
    current_content: list[
        openai_types.ChatCompletionContentPartTextParam
        | openai_types.ChatCompletionContentPartImageParam
        | openai_types.ChatCompletionContentPartInputAudioParam
    ] = []
    result: list[openai_types.ChatCompletionMessageParam] = []

    def flush_message_content() -> None:
        nonlocal current_content
        if current_content:
            if len(current_content) == 1 and current_content[0]["type"] == "text":
                result.append(
                    openai_types.ChatCompletionUserMessageParam(
                        role="user", content=current_content[0]["text"]
                    )
                )
            else:
                result.append(
                    openai_types.ChatCompletionUserMessageParam(
                        role="user", content=current_content
                    )
                )
            current_content = []

    for part in message.content:
        if part.type == "text":
            current_content.append(
                openai_types.ChatCompletionContentPartTextParam(
                    text=part.text, type="text"
                )
            )
        elif part.type == "image":
            url = (
                part.source.url
                if part.source.type == "url_image_source"
                else f"data:{part.source.mime_type};base64,{part.source.data}"
            )
            content = openai_types.ChatCompletionContentPartImageParam(
                type="image_url", image_url={"url": url, "detail": "auto"}
            )
            current_content.append(content)
        elif part.type == "audio":
            base_model_name = model_name(model_id, None)
            if base_model_name in MODELS_WITHOUT_AUDIO_SUPPORT:
                raise FeatureNotSupportedError(
                    feature="Audio inputs",
                    provider_id="openai",
                    message=f"Model '{model_id}' does not support audio inputs.",
                )

            if part.source.type == "base64_audio_source":
                audio_format = part.source.mime_type.split("/")[1]
                if audio_format not in ("wav", "mp3"):
                    raise FeatureNotSupportedError(
                        feature=f"Audio format: {audio_format}",
                        provider_id="openai",
                        message="OpenAI only supports 'wav' and 'mp3' audio formats.",
                    )  # pragma: no cover
                audio_content = openai_types.ChatCompletionContentPartInputAudioParam(
                    type="input_audio",
                    input_audio={
                        "data": part.source.data,
                        "format": audio_format,
                    },
                )
                current_content.append(audio_content)
        elif part.type == "tool_output":
            flush_message_content()
            result.append(
                openai_types.ChatCompletionToolMessageParam(
                    role="tool",
                    content=str(part.value),
                    tool_call_id=part.id,
                )
            )
        else:
            raise NotImplementedError(
                f"Unsupported user content part type: {part.type}"
            )
    flush_message_content()

    return result


def _encode_assistant_message(
    message: AssistantMessage, model_id: OpenAIModelId, encode_thoughts: bool
) -> openai_types.ChatCompletionAssistantMessageParam:
    """Convert Mirascope `AssistantMessage` to OpenAI `ChatCompletionAssistantMessageParam`."""

    if (
        message.provider_id in ("openai", "openai:completions")
        and message.provider_model_name
        == model_name(model_id=model_id, api_mode="completions")
        and message.raw_message
        and not encode_thoughts
    ):
        return cast(
            openai_types.ChatCompletionAssistantMessageParam, message.raw_message
        )

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
        elif part.type == "thought":
            if encode_thoughts:
                text_params.append(
                    openai_types.ChatCompletionContentPartTextParam(
                        text="**Thinking:** " + part.thought, type="text"
                    )
                )
        else:
            raise NotImplementedError(f"Unsupported content type: {part.type}")

    content: str | list[openai_types.ChatCompletionContentPartTextParam] | None = None
    if len(text_params) == 1:
        content = text_params[0]["text"]
    elif text_params:
        content = text_params

    message_params: openai_types.ChatCompletionAssistantMessageParam = {
        "role": "assistant",
        "content": content,
    }
    if tool_call_params:
        message_params["tool_calls"] = tool_call_params

    return openai_types.ChatCompletionAssistantMessageParam(**message_params)


def _encode_message(
    message: Message, model_id: OpenAIModelId, encode_thoughts: bool
) -> list[openai_types.ChatCompletionMessageParam]:
    """Convert a Mirascope `Message` to OpenAI `ChatCompletionMessageParam` format.

    Args:
        message: A Mirascope message (system, user, or assistant)
        model_id: The model ID being used
        encode_thoughts: Whether to encode thoughts as text

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
        return _encode_user_message(message, model_id)
    elif message.role == "assistant":
        return [_encode_assistant_message(message, model_id, encode_thoughts)]
    else:
        raise ValueError(f"Unsupported role: {message.role}")  # pragma: no cover


@lru_cache(maxsize=128)
def _convert_tool_to_tool_param(
    tool: AnyToolSchema,
) -> openai_types.ChatCompletionToolParam:
    """Convert a single Mirascope `Tool` to OpenAI ChatCompletionToolParam with caching."""
    schema_dict = tool.parameters.model_dump(by_alias=True, exclude_none=True)
    schema_dict["type"] = "object"
    _base_utils.ensure_additional_properties_false(schema_dict)
    return openai_types.ChatCompletionToolParam(
        type="function",
        function={
            "name": tool.name,
            "description": tool.description,
            "parameters": schema_dict,
            "strict": tool.strict,
        },
    )


def _create_strict_response_format(
    format: Format[FormattableT],
) -> shared_openai_types.ResponseFormatJSONSchema:
    """Create OpenAI strict response format from a Mirascope Format.

    Args:
        format: The `Format` instance containing schema and metadata

    Returns:
        Dictionary containing OpenAI response_format specification
    """
    schema = format.schema.copy()

    _base_utils.ensure_additional_properties_false(schema)

    json_schema = JSONSchema(
        name=format.name,
        schema=schema,
        strict=True,
    )
    if format.description:
        json_schema["description"] = format.description

    return shared_openai_types.ResponseFormatJSONSchema(
        type="json_schema", json_schema=json_schema
    )


def encode_request(
    *,
    model_id: OpenAIModelId,
    messages: Sequence[Message],
    tools: Sequence[AnyToolSchema] | BaseToolkit[AnyToolSchema] | None,
    format: type[FormattableT] | Format[FormattableT] | None,
    params: Params,
) -> tuple[Sequence[Message], Format[FormattableT] | None, ChatCompletionCreateKwargs]:
    """Prepares a request for the `OpenAI.chat.completions.create` method."""
    if model_id.endswith(":responses"):
        raise FeatureNotSupportedError(
            feature="responses API",
            provider_id="openai:completions",
            model_id=model_id,
            message=f"Can't use completions client for responses model: {model_id}",
        )
    base_model_name = model_name(model_id, None)

    kwargs: ChatCompletionCreateKwargs = ChatCompletionCreateKwargs(
        {
            "model": base_model_name,
        }
    )
    encode_thoughts = False

    with _base_utils.ensure_all_params_accessed(
        params=params,
        provider_id="openai",
        unsupported_params=["top_k", "thinking"],
    ) as param_accessor:
        if param_accessor.temperature is not None:
            kwargs["temperature"] = param_accessor.temperature
        if param_accessor.max_tokens is not None:
            kwargs["max_tokens"] = param_accessor.max_tokens
        if param_accessor.top_p is not None:
            kwargs["top_p"] = param_accessor.top_p

        if param_accessor.seed is not None:
            kwargs["seed"] = param_accessor.seed
        if param_accessor.stop_sequences is not None:
            kwargs["stop"] = param_accessor.stop_sequences
        if param_accessor.encode_thoughts_as_text is not None:
            encode_thoughts = True

    tools = tools.tools if isinstance(tools, BaseToolkit) else tools or []

    openai_tools = [_convert_tool_to_tool_param(tool) for tool in tools]

    model_supports_strict = base_model_name not in MODELS_WITHOUT_JSON_SCHEMA_SUPPORT
    default_mode = "strict" if model_supports_strict else "tool"
    format = resolve_format(format, default_mode=default_mode)
    if format is not None:
        if format.mode == "strict":
            if not model_supports_strict:
                raise FormattingModeNotSupportedError(
                    formatting_mode="strict",
                    provider_id="openai",
                    model_id=model_id,
                )
            kwargs["response_format"] = _create_strict_response_format(format)
        elif format.mode == "tool":
            if tools:
                kwargs["tool_choice"] = "required"
            else:
                kwargs["tool_choice"] = {
                    "type": "function",
                    "function": {"name": FORMAT_TOOL_NAME},
                }
                kwargs["parallel_tool_calls"] = False
            format_tool_schema = _formatting_utils.create_tool_schema(format)
            openai_tools.append(_convert_tool_to_tool_param(format_tool_schema))
        elif (
            format.mode == "json"
            and base_model_name not in MODELS_WITHOUT_JSON_OBJECT_SUPPORT
        ):
            kwargs["response_format"] = {"type": "json_object"}

        if format.formatting_instructions:
            messages = _base_utils.add_system_instructions(
                messages, format.formatting_instructions
            )

    if openai_tools:
        kwargs["tools"] = openai_tools

    encoded_messages: list[openai_types.ChatCompletionMessageParam] = []
    for message in messages:
        encoded_messages.extend(_encode_message(message, model_id, encode_thoughts))
    kwargs["messages"] = encoded_messages

    return messages, format, kwargs
