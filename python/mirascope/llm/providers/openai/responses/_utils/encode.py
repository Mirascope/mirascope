"""OpenAI Responses message encoding and request preparation."""

from collections.abc import Sequence
from typing import TypedDict, cast

from openai import Omit
from openai.types.responses import (
    FunctionToolParam,
    ResponseFormatTextJSONSchemaConfigParam,
    ResponseFunctionToolCallParam,
    ResponseInputContentParam,
    ResponseInputItemParam,
    ResponseInputParam,
    ResponseInputTextParam,
    ResponseTextConfigParam,
    ToolChoiceAllowedParam,
    ToolChoiceFunctionParam,
    response_create_params,
)
from openai.types.responses.easy_input_message_param import EasyInputMessageParam
from openai.types.responses.response_input_image_param import ResponseInputImageParam
from openai.types.responses.response_input_param import (
    FunctionCallOutput,
    Message as ResponseInputMessageParam,
)
from openai.types.shared_params import Reasoning
from openai.types.shared_params.response_format_json_object import (
    ResponseFormatJSONObject,
)
from openai.types.shared_params.responses_model import ResponsesModel

from .....exceptions import FeatureNotSupportedError
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
    MODELS_WITHOUT_JSON_OBJECT_SUPPORT,
    MODELS_WITHOUT_JSON_SCHEMA_SUPPORT,
    NON_REASONING_MODELS,
)


class ResponseCreateKwargs(TypedDict, total=False):
    """Kwargs to the OpenAI `client.responses.create` method."""

    model: ResponsesModel
    input: str | ResponseInputParam
    instructions: str
    temperature: float
    max_output_tokens: int
    top_p: float
    tools: list[FunctionToolParam] | Omit
    tool_choice: response_create_params.ToolChoice | Omit
    text: ResponseTextConfigParam
    reasoning: Reasoning | Omit


def _encode_user_message(
    message: UserMessage,
) -> ResponseInputParam:
    if len(message.content) == 1 and (first := message.content[0]).type == "text":
        return [EasyInputMessageParam(content=first.text, role="user")]

    current_content: list[ResponseInputContentParam] = []
    result: ResponseInputParam = []

    def flush_message_content() -> None:
        nonlocal current_content
        if current_content:
            result.append(
                ResponseInputMessageParam(
                    content=current_content, role="user", type="message"
                )
            )
            current_content = []

    for part in message.content:
        if part.type == "text":
            current_content.append(
                ResponseInputTextParam(text=part.text, type="input_text")
            )
        elif part.type == "image":
            image_url = (
                part.source.url
                if part.source.type == "url_image_source"
                else f"data:{part.source.mime_type};base64,{part.source.data}"
            )

            current_content.append(
                ResponseInputImageParam(
                    image_url=image_url, detail="auto", type="input_image"
                )
            )
        elif part.type == "tool_output":
            flush_message_content()
            result.append(
                FunctionCallOutput(
                    call_id=part.id,
                    output=str(part.value),
                    type="function_call_output",
                )
            )
        elif part.type == "audio":
            raise FeatureNotSupportedError(
                "audio input",
                "openai",
                message='provider "openai" does not support audio inputs when using :responses api. Try appending :completions to your model instead.',
            )
        else:
            raise NotImplementedError(
                f"Unsupported user content part type: {part.type}"
            )
    flush_message_content()

    return result


def _encode_assistant_message(
    message: AssistantMessage, encode_thoughts: bool
) -> ResponseInputParam:
    result: ResponseInputParam = []

    # Note: OpenAI does not provide any way to encode multiplie pieces of assistant-generated
    # text as adjacent content within the same Message, except as part of
    # ResponseOutputMessageParam which requires OpenAI-provided `id` and `status` on the message,
    # and `annotations` and `logprobs` on the output text.
    # Rather than generating a fake or nonexistent fields and triggering potentially undefined
    # server-side behavior, we use `EasyInputMessageParam` for assistant generated text,
    # with the caveat that assistant messages containing multiple text parts will be encoded
    # as though they are separate messages.
    # (It would seem as though the `Message` class in `response_input_param.py` would be suitable,
    # especially as it supports the "assistant" role; however attempting to use it triggers a server
    # error when text of type input_text is passed as part of an assistant message.)
    for part in message.content:
        if part.type == "text":
            result.append(EasyInputMessageParam(content=part.text, role="assistant"))
        elif part.type == "thought":
            if encode_thoughts:
                result.append(
                    EasyInputMessageParam(
                        content="**Thinking:** " + part.thought, role="assistant"
                    )
                )
        elif part.type == "tool_call":
            result.append(
                ResponseFunctionToolCallParam(
                    call_id=part.id,
                    name=part.name,
                    arguments=part.args,
                    type="function_call",
                )
            )
        else:
            raise NotImplementedError(
                f"Unsupported assistant content part type: {part.type}"
            )

    return result


def _encode_message(
    message: Message, model_id: OpenAIModelId, encode_thoughts: bool
) -> ResponseInputParam:
    """Convert a Mirascope Message to OpenAI Responses input items.

    Returns a list because tool calls and tool outputs become separate input items
    in the Responses API, not part of message content.
    """

    if message.role == "system":
        # Responses API allows multiple "developer" messages, so rather than using the
        # instructions field, we convert system messages as we find them.
        # Unlike other LLM APIs, the system message does not need to be the first message.
        return [EasyInputMessageParam(role="developer", content=message.content.text)]

    if (
        message.role == "assistant"
        and message.provider_id in ("openai", "openai:responses")
        and message.provider_model_name
        == model_name(model_id=model_id, api_mode="responses")
        and message.raw_message
        and not encode_thoughts
    ):
        return cast(ResponseInputParam, message.raw_message)

    if message.role == "assistant":
        return _encode_assistant_message(message, encode_thoughts)
    else:
        return _encode_user_message(message)


def _convert_tool_to_function_tool_param(tool: AnyToolSchema) -> FunctionToolParam:
    """Convert a Mirascope ToolSchema to OpenAI Responses FunctionToolParam."""
    schema_dict = tool.parameters.model_dump(by_alias=True, exclude_none=True)
    schema_dict["type"] = "object"
    _base_utils.ensure_additional_properties_false(schema_dict)

    return FunctionToolParam(
        type="function",
        name=tool.name,
        description=tool.description,
        parameters=schema_dict,
        strict=tool.strict,
    )


def _create_strict_response_format(
    format: Format[FormattableT],
) -> ResponseFormatTextJSONSchemaConfigParam:
    """Create OpenAI Responses strict response format from a Mirascope Format.

    Args:
        format: The `Format` instance containing schema and metadata

    Returns:
        ResponseFormatTextJSONSchemaConfigParam for strict structured outputs
    """
    schema = format.schema.copy()
    _base_utils.ensure_additional_properties_false(schema)

    response_format: ResponseFormatTextJSONSchemaConfigParam = {
        "type": "json_schema",
        "name": format.name,
        "schema": schema,
    }
    if format.description:
        response_format["description"] = format.description
    response_format["strict"] = True

    return response_format


def _compute_reasoning(thinking: bool) -> Reasoning:
    """Compute the OpenAI `Reasoning` config based on thinking settings."""
    if thinking:
        return {"effort": "medium", "summary": "auto"}
    else:
        return {"effort": "minimal"}


def encode_request(
    *,
    model_id: OpenAIModelId,
    messages: Sequence[Message],
    tools: Sequence[AnyToolSchema] | BaseToolkit[AnyToolSchema] | None,
    format: type[FormattableT] | Format[FormattableT] | None,
    params: Params,
) -> tuple[Sequence[Message], Format[FormattableT] | None, ResponseCreateKwargs]:
    """Prepares a request for the `OpenAI.responses.create` method."""
    if model_id.endswith(":completions"):
        raise FeatureNotSupportedError(
            feature="completions API",
            provider_id="openai:responses",
            model_id=model_id,
            message=f"Cannot use completions model with responses client: {model_id}",
        )

    base_model_name = model_name(model_id, None)

    kwargs: ResponseCreateKwargs = ResponseCreateKwargs(
        {
            "model": base_model_name,
        }
    )
    encode_thoughts = False

    with _base_utils.ensure_all_params_accessed(
        params=params,
        provider_id="openai",
        unsupported_params=["top_k", "seed", "stop_sequences"],
    ) as param_accessor:
        if param_accessor.temperature is not None:
            kwargs["temperature"] = param_accessor.temperature
        if param_accessor.max_tokens is not None:
            kwargs["max_output_tokens"] = param_accessor.max_tokens
        if param_accessor.top_p is not None:
            kwargs["top_p"] = param_accessor.top_p
        if param_accessor.thinking is not None:
            if base_model_name in NON_REASONING_MODELS:
                param_accessor.emit_warning_for_unused_param(
                    "thinking", param_accessor.thinking, "openai", model_id
                )
            else:
                # Assume model supports reasoning unless explicitly listed as non-reasoning
                # This ensures new reasoning models work immediately without code updates
                kwargs["reasoning"] = _compute_reasoning(param_accessor.thinking)
        if param_accessor.encode_thoughts_as_text:
            encode_thoughts = True

    tools = tools.tools if isinstance(tools, BaseToolkit) else tools or []
    openai_tools = [_convert_tool_to_function_tool_param(tool) for tool in tools]

    model_supports_strict = model_id not in MODELS_WITHOUT_JSON_SCHEMA_SUPPORT
    default_mode = "strict" if model_supports_strict else "tool"

    format = resolve_format(format, default_mode=default_mode)
    if format is not None:
        if format.mode == "strict":
            kwargs["text"] = {"format": _create_strict_response_format(format)}
        elif format.mode == "tool":
            format_tool_shared_utils = _formatting_utils.create_tool_schema(format)
            openai_tools.append(
                _convert_tool_to_function_tool_param(format_tool_shared_utils)
            )
            if tools:
                kwargs["tool_choice"] = ToolChoiceAllowedParam(
                    type="allowed_tools",
                    mode="required",
                    tools=[
                        {"type": "function", "name": tool["name"]}
                        for tool in openai_tools
                    ],
                )
            else:
                kwargs["tool_choice"] = ToolChoiceFunctionParam(
                    type="function",
                    name=FORMAT_TOOL_NAME,
                )
        elif (
            format.mode == "json" and model_id not in MODELS_WITHOUT_JSON_OBJECT_SUPPORT
        ):
            kwargs["text"] = {"format": ResponseFormatJSONObject(type="json_object")}

        if format.formatting_instructions:
            messages = _base_utils.add_system_instructions(
                messages, format.formatting_instructions
            )

    encoded_messages: list[ResponseInputItemParam] = []
    for message in messages:
        encoded_messages.extend(_encode_message(message, model_id, encode_thoughts))
    kwargs["input"] = encoded_messages

    if openai_tools:
        kwargs["tools"] = openai_tools

    return messages, format, kwargs
