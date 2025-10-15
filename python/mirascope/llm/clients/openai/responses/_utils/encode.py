"""OpenAI Responses message encoding and request preparation."""

from collections.abc import Sequence
from typing import TypedDict, cast

from openai import NotGiven
from openai.types import responses as openai_types
from openai.types.responses import response_create_params
from openai.types.responses.easy_input_message_param import EasyInputMessageParam
from openai.types.responses.function_tool_param import FunctionToolParam
from openai.types.responses.response_format_text_json_schema_config_param import (
    ResponseFormatTextJSONSchemaConfigParam,
)
from openai.types.responses.response_function_tool_call_param import (
    ResponseFunctionToolCallParam,
)
from openai.types.responses.response_input_param import (
    FunctionCallOutput,
    ResponseInputItemParam,
    ResponseInputParam,
)
from openai.types.responses.response_text_config_param import ResponseTextConfigParam
from openai.types.responses.tool_choice_allowed_param import ToolChoiceAllowedParam
from openai.types.responses.tool_choice_function_param import ToolChoiceFunctionParam
from openai.types.shared_params import Reasoning
from openai.types.shared_params.response_format_json_object import (
    ResponseFormatJSONObject,
)
from openai.types.shared_params.responses_model import ResponsesModel

from .....formatting import (
    Format,
    FormattableT,
    _utils as _formatting_utils,
    resolve_format,
)
from .....messages import Message
from .....tools import FORMAT_TOOL_NAME, BaseToolkit, ToolSchema
from ....base import Params, _utils as _base_utils
from ...shared import _utils as _shared_utils
from ..model_ids import OpenAIResponsesModelId
from ..model_info import NON_REASONING_MODELS


class ResponseCreateKwargs(TypedDict, total=False):
    """Kwargs to the OpenAI `client.responses.create` method."""

    model: ResponsesModel
    input: str | openai_types.ResponseInputParam
    instructions: str
    temperature: float
    max_output_tokens: int
    top_p: float
    tools: list[FunctionToolParam] | NotGiven
    tool_choice: response_create_params.ToolChoice | NotGiven
    text: ResponseTextConfigParam
    reasoning: Reasoning | NotGiven


def _encode_message(
    message: Message, model_id: OpenAIResponsesModelId, encode_thoughts: bool
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
        and message.provider == "openai:responses"
        and message.model_id == model_id
        and message.raw_content
    ):
        message_has_thoughts = any(
            content.type == "thought" for content in message.content
        )
        if not (encode_thoughts and message_has_thoughts):
            return cast(ResponseInputParam, message.raw_content)

    result: ResponseInputParam = []

    for part in message.content:
        if part.type == "text":
            result.append(EasyInputMessageParam(role=message.role, content=part.text))
        elif part.type == "tool_call":
            result.append(
                ResponseFunctionToolCallParam(
                    call_id=part.id,
                    name=part.name,
                    arguments=part.args,
                    type="function_call",
                )
            )
        elif part.type == "tool_output":
            result.append(
                FunctionCallOutput(
                    call_id=part.id,
                    output=str(part.value),
                    type="function_call_output",
                )
            )
        elif part.type == "thought" and encode_thoughts:
            result.append(
                EasyInputMessageParam(
                    role=message.role, content="**Thinking:** " + part.thought
                )
            )
        else:
            raise NotImplementedError(f"Unsupported content part type: {part.type}")

    return result


def _convert_tool_to_function_tool_param(tool: ToolSchema) -> FunctionToolParam:
    """Convert a Mirascope ToolSchema to OpenAI Responses FunctionToolParam."""
    schema_dict = tool.parameters.model_dump(by_alias=True, exclude_none=True)
    schema_dict["type"] = "object"
    _shared_utils._ensure_additional_properties_false(schema_dict)

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
    _shared_utils._ensure_additional_properties_false(schema)

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
    model_id: OpenAIResponsesModelId,
    messages: Sequence[Message],
    tools: Sequence[ToolSchema] | BaseToolkit | None,
    format: type[FormattableT] | Format[FormattableT] | None,
    params: Params,
) -> tuple[Sequence[Message], Format[FormattableT] | None, ResponseCreateKwargs]:
    """Prepares a request for the `OpenAI.responses.create` method."""
    kwargs: ResponseCreateKwargs = ResponseCreateKwargs(
        {
            "model": model_id,
        }
    )
    encode_thoughts = False

    with _base_utils.ensure_all_params_accessed(
        params=params,
        provider="openai:responses",
        unsupported_params=["top_k", "seed", "stop_sequences"],
    ) as param_accessor:
        if param_accessor.temperature is not None:
            kwargs["temperature"] = param_accessor.temperature
        if param_accessor.max_tokens is not None:
            kwargs["max_output_tokens"] = param_accessor.max_tokens
        if param_accessor.top_p is not None:
            kwargs["top_p"] = param_accessor.top_p
        if param_accessor.thinking is not None:
            thinking = param_accessor.thinking
            if model_id in NON_REASONING_MODELS:
                param_accessor.emit_warning_for_unused_param(
                    "thinking", param_accessor.thinking, "openai:responses", model_id
                )
            else:
                # Assume model supports reasoning unless explicitly listed as non-reasoning
                # This ensures new reasoning models work immediately without code updates
                kwargs["reasoning"] = _compute_reasoning(thinking)
        if param_accessor.encode_thoughts_as_text:
            encode_thoughts = True

    tools = tools.tools if isinstance(tools, BaseToolkit) else tools or []
    openai_tools = [_convert_tool_to_function_tool_param(tool) for tool in tools]

    model_supports_strict = (
        model_id not in _shared_utils.MODELS_WITHOUT_JSON_SCHEMA_SUPPORT
    )
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
            format.mode == "json"
            and model_id not in _shared_utils.MODELS_WITHOUT_JSON_OBJECT_SUPPORT
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
