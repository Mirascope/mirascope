"""OpenAI completions message encoding and request preparation."""

from __future__ import annotations

from collections.abc import Sequence
from functools import lru_cache
from typing import TYPE_CHECKING, TypedDict, cast

from openai import Omit
from openai.types import chat as openai_types, shared_params as shared_openai_types
from openai.types.shared_params.response_format_json_schema import JSONSchema

from .....content import Document
from .....exceptions import FeatureNotSupportedError
from .....formatting import Format, FormatSpec, FormattableT, resolve_format
from .....messages import AssistantMessage, Message, UserMessage
from .....tools import (
    FORMAT_TOOL_NAME,
    AnyToolSchema,
    BaseToolkit,
    ProviderTool,
    WebSearchTool,
)
from ....base import _utils as _base_utils
from ...model_id import OpenAIModelId, model_name
from .feature_info import CompletionsModelFeatureInfo

if TYPE_CHECKING:
    from .....models import Params


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
    max_completion_tokens: int | Omit
    top_p: float | Omit
    seed: int | Omit
    stop: str | list[str] | Omit
    reasoning_effort: shared_openai_types.ReasoningEffort | Omit


def _encode_document(
    doc: Document,
    provider_id: str,
) -> openai_types.ChatCompletionContentPartParam:
    """Encode a Document content part to OpenAI Completions API format.

    Raises:
        FeatureNotSupportedError: If the document uses a URL source.
    """
    import base64 as _base64

    from openai.types.chat.chat_completion_content_part_param import File, FileFile

    source = doc.source
    if source.type == "base64_document_source":
        return File(
            type="file",
            file=FileFile(
                file_data=f"data:{source.media_type};base64,{source.data}",
                filename="document.pdf",
            ),
        )
    elif source.type == "text_document_source":
        encoded = _base64.b64encode(source.data.encode("utf-8")).decode("utf-8")
        return File(
            type="file",
            file=FileFile(
                file_data=f"data:{source.media_type};base64,{encoded}",
                filename="document.txt",
            ),
        )
    else:  # url_document_source
        raise FeatureNotSupportedError(
            "url_document_source",
            provider_id,
            message=f"Provider '{provider_id}' does not support URL-referenced documents. Use `Document.from_file(...)` or `Document.from_bytes(...)` instead.",
        )


def _encode_user_message(
    message: UserMessage,
    model_id: OpenAIModelId,
    feature_info: CompletionsModelFeatureInfo,
    provider_id: str,
) -> list[openai_types.ChatCompletionMessageParam]:
    """Convert Mirascope `UserMessage` to a list of OpenAI `ChatCompletionMessageParam`.

    Multiple text content parts are combined into a single user message.
    Tool outputs become separate tool messages.
    """
    current_content: list[openai_types.ChatCompletionContentPartParam] = []
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
            if feature_info.audio_support is False:
                raise FeatureNotSupportedError(
                    feature="Audio inputs",
                    provider_id=provider_id,
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
        elif part.type == "document":
            current_content.append(_encode_document(part, provider_id))
        elif part.type == "tool_output":
            flush_message_content()
            result.append(
                openai_types.ChatCompletionToolMessageParam(
                    role="tool",
                    content=str(part.result),
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
    message: AssistantMessage, model_id: OpenAIModelId, encode_thoughts_as_text: bool
) -> openai_types.ChatCompletionAssistantMessageParam:
    """Convert Mirascope `AssistantMessage` to OpenAI `ChatCompletionAssistantMessageParam`."""

    if (
        message.provider_id in ("openai", "openai:completions")
        and message.provider_model_name
        == model_name(model_id=model_id, api_mode="completions")
        and message.raw_message
        and not encode_thoughts_as_text
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
            if encode_thoughts_as_text:
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
    message: Message,
    model_id: OpenAIModelId,
    encode_thoughts_as_text: bool,
    feature_info: CompletionsModelFeatureInfo,
    provider_id: str,
) -> list[openai_types.ChatCompletionMessageParam]:
    """Convert a Mirascope `Message` to OpenAI `ChatCompletionMessageParam` format."""
    if message.role == "system":
        return [
            openai_types.ChatCompletionSystemMessageParam(
                role="system", content=message.content.text
            )
        ]
    elif message.role == "user":
        return _encode_user_message(message, model_id, feature_info, provider_id)
    elif message.role == "assistant":
        return [_encode_assistant_message(message, model_id, encode_thoughts_as_text)]
    else:
        raise ValueError(f"Unsupported role: {message.role}")  # pragma: no cover


@lru_cache(maxsize=128)
def _convert_tool_to_tool_param(
    tool: AnyToolSchema | ProviderTool,
) -> openai_types.ChatCompletionToolParam:
    """Convert a single Mirascope `Tool` to OpenAI ChatCompletionToolParam with caching."""
    if isinstance(tool, WebSearchTool):
        raise FeatureNotSupportedError(
            "WebSearchTool",
            provider_id="openai:completions",
            message="Web search is only available in the OpenAI Responses API. "
            "Use a model with :responses suffix (e.g., 'openai/gpt-4o:responses').",
        )
    if isinstance(tool, ProviderTool):
        raise FeatureNotSupportedError(
            f"Provider tool {tool.name}", provider_id="openai:completions"
        )
    schema_dict = tool.parameters.model_dump(by_alias=True, exclude_none=True)
    schema_dict["type"] = "object"
    _base_utils.ensure_additional_properties_false(schema_dict)
    strict = True if tool.strict is None else tool.strict
    if strict:
        _base_utils.ensure_all_properties_required(schema_dict)
    return openai_types.ChatCompletionToolParam(
        type="function",
        function={
            "name": tool.name,
            "description": tool.description,
            "parameters": schema_dict,
            "strict": strict,
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
    tools: BaseToolkit[AnyToolSchema],
    format: FormatSpec[FormattableT] | None,
    params: Params,
    feature_info: CompletionsModelFeatureInfo,
    provider_id: str,
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

    is_reasoning_model = feature_info.is_reasoning_model is True
    strict_supported = feature_info.strict_support is True
    strict_allowed = feature_info.strict_support is not False
    supports_json_object = feature_info.json_object_support is True

    kwargs: ChatCompletionCreateKwargs = ChatCompletionCreateKwargs(
        {"model": base_model_name}
    )
    encode_thoughts_as_text = False

    with _base_utils.ensure_all_params_accessed(
        params=params,
        provider_id=provider_id,
        unsupported_params=[
            "top_k",
            *(["temperature", "top_p", "stop_sequences"] if is_reasoning_model else []),
        ],
    ) as param_accessor:
        if not is_reasoning_model and param_accessor.temperature is not None:
            kwargs["temperature"] = param_accessor.temperature
        if param_accessor.max_tokens is not None:
            if is_reasoning_model:
                kwargs["max_completion_tokens"] = param_accessor.max_tokens
            else:
                kwargs["max_tokens"] = param_accessor.max_tokens
        if not is_reasoning_model and param_accessor.top_p is not None:
            kwargs["top_p"] = param_accessor.top_p

        if param_accessor.seed is not None:
            kwargs["seed"] = param_accessor.seed
        if not is_reasoning_model and param_accessor.stop_sequences is not None:
            kwargs["stop"] = param_accessor.stop_sequences
        if param_accessor.thinking is not None:
            thinking = param_accessor.thinking
            if thinking.get("encode_thoughts_as_text"):
                encode_thoughts_as_text = True

    openai_tools = [_convert_tool_to_tool_param(tool) for tool in tools.tools]

    default_mode = "strict" if strict_supported else "tool"
    format = resolve_format(format, default_mode=default_mode)
    if format is not None:
        if format.mode == "strict":
            if not strict_allowed:
                raise FeatureNotSupportedError(
                    feature="formatting_mode:strict",
                    provider_id=provider_id,
                    model_id=model_id,
                )
            kwargs["response_format"] = _create_strict_response_format(format)
        elif format.mode == "tool":
            if tools.tools:
                kwargs["tool_choice"] = "required"
            else:
                kwargs["tool_choice"] = {
                    "type": "function",
                    "function": {"name": FORMAT_TOOL_NAME},
                }
                kwargs["parallel_tool_calls"] = False
            format_tool_schema = format.create_tool_schema()
            openai_tools.append(_convert_tool_to_tool_param(format_tool_schema))
        elif format.mode == "json" and supports_json_object:
            kwargs["response_format"] = {"type": "json_object"}

        if format.formatting_instructions:
            messages = _base_utils.add_system_instructions(
                messages, format.formatting_instructions
            )

    if openai_tools:
        kwargs["tools"] = openai_tools

    encoded_messages: list[openai_types.ChatCompletionMessageParam] = []
    for message in messages:
        encoded_messages.extend(
            _encode_message(
                message, model_id, encode_thoughts_as_text, feature_info, provider_id
            )
        )
    kwargs["messages"] = encoded_messages

    return messages, format, kwargs
