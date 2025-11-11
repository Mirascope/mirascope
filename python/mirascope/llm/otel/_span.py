"""Context manager for emitting OpenTelemetry GenAI spans."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from opentelemetry.trace import Span as SpanT, SpanKind, Status, StatusCode, Tracer
    from opentelemetry.util.types import AttributeValue
else:
    AttributeValue = None
    SpanT = None
    Tracer = None


try:
    from opentelemetry import trace
    from opentelemetry.trace import SpanKind, Status, StatusCode
except ImportError:  # pragma: no cover
    trace = None

    if not TYPE_CHECKING:

        class SpanKindPlaceholder:
            CLIENT: int = 1

        class StatusCodePlaceholder:
            ERROR: int = 2

        class StatusPlaceholder:
            def __init__(self, code: int, description: str = "") -> None:
                self.code = code
                self.description = description

        SpanKind = SpanKindPlaceholder()
        StatusCode = StatusCodePlaceholder()
        Status = StatusPlaceholder

from opentelemetry.semconv._incubating.attributes import (
    gen_ai_attributes as GenAIAttributes,
)
from opentelemetry.semconv.attributes import (
    error_attributes as ErrorAttributes,
)

from ..formatting import Format
from ..formatting._utils import create_tool_schema
from ..messages import Message
from ..responses.root_response import RootResponse
from ..tools.tool_schema import ToolSchema
from ..tools.toolkit import BaseToolkit
from ._json import json_dumps
from ._messages import (
    finish_reason_to_string,
    serialize_response_messages,
    split_request_messages,
)

TRACER: Tracer | None = None


def set_tracer(tracer: Tracer | None) -> None:
    global TRACER
    TRACER = tracer


def get_tracer() -> Tracer | None:
    return TRACER


RequestMessages: TypeAlias = Sequence[Message]
ResponseT: TypeAlias = RootResponse
ToolsParam: TypeAlias = Sequence[ToolSchema | type] | BaseToolkit | None
FormatParam: TypeAlias = Format | type | None
ParamsDict: TypeAlias = Mapping[str, str | int | float | bool | Sequence[str] | None]
SpanAttributes: TypeAlias = Mapping[str, AttributeValue]


@contextmanager
def span(
    *,
    operation: str,
    provider: str,
    model_id: str,
    messages: RequestMessages,
    tools: ToolsParam,
    format: FormatParam,
    params: ParamsDict,
) -> Iterator[SpanT | None]:
    tracer = get_tracer()
    if tracer is None or trace is None:
        yield None
        return

    attrs = build_request_attributes(
        operation=operation,
        provider=provider,
        model_id=model_id,
        messages=messages,
        tools=tools,
        format=format,
        params=params,
    )

    with tracer.start_as_current_span(
        name=f"{operation} {model_id}",
        kind=SpanKind.CLIENT,
    ) as active_span:
        assign_attributes(active_span, attrs)
        try:
            yield active_span
        except Exception as exc:
            record_exception(active_span, exc)
            raise


def assign_attributes(span: SpanT | None, attributes: SpanAttributes) -> None:
    """Set multiple attributes on a span."""
    if span is None:
        return
    for key, value in attributes.items():
        span.set_attribute(key, value)


def record_exception(span: SpanT | None, exc: Exception) -> None:
    """Record exception details on span following OpenTelemetry semantic conventions."""
    if span is None:
        return
    span.record_exception(exc)
    span.set_attribute(ErrorAttributes.ERROR_TYPE, exc.__class__.__name__)
    error_message = str(exc)
    if error_message:
        span.set_attribute("error.message", error_message)
    span.set_status(Status(StatusCode.ERROR, error_message))


def attach_response(
    span: SpanT,
    response: ResponseT,
    *,
    request_messages: RequestMessages,
) -> None:
    span.set_attribute(GenAIAttributes.GEN_AI_RESPONSE_MODEL, response.model_id)
    span.set_attribute(
        GenAIAttributes.GEN_AI_RESPONSE_FINISH_REASONS,
        [finish_reason_to_string(response.finish_reason)],
    )
    response_id = extract_response_id(response.raw)
    if response_id:
        span.set_attribute(GenAIAttributes.GEN_AI_RESPONSE_ID, response_id)

    serialized = serialize_response_messages(response)
    output_json = serialized.get(GenAIAttributes.GEN_AI_OUTPUT_MESSAGES)
    if output_json:
        span.set_attribute(GenAIAttributes.GEN_AI_OUTPUT_MESSAGES, output_json)
    # TODO: Emit gen_ai.usage metrics once Response exposes provider-agnostic usage fields.

    system, inputs = split_request_messages(request_messages)
    system_payload = system
    if system_payload:
        span.set_attribute(
            GenAIAttributes.GEN_AI_SYSTEM_INSTRUCTIONS, json_dumps(system_payload)
        )
    input_payload = inputs
    if input_payload:
        span.set_attribute(
            GenAIAttributes.GEN_AI_INPUT_MESSAGES, json_dumps(input_payload)
        )


def build_request_attributes(
    *,
    operation: str,
    provider: str,
    model_id: str,
    messages: RequestMessages,
    tools: ToolsParam,
    format: FormatParam,
    params: ParamsDict,
) -> dict[str, AttributeValue]:
    attrs: dict[str, AttributeValue] = {
        GenAIAttributes.GEN_AI_OPERATION_NAME: operation,
        GenAIAttributes.GEN_AI_PROVIDER_NAME: provider,
        GenAIAttributes.GEN_AI_REQUEST_MODEL: model_id,
        GenAIAttributes.GEN_AI_OUTPUT_TYPE: infer_output_type(format),
    }
    apply_param_attributes(attrs, params)

    system, inputs = split_request_messages(messages)
    system_payload = system
    input_payload = inputs
    if system_payload:
        attrs[GenAIAttributes.GEN_AI_SYSTEM_INSTRUCTIONS] = json_dumps(system_payload)
    if input_payload:
        attrs[GenAIAttributes.GEN_AI_INPUT_MESSAGES] = json_dumps(input_payload)

    tool_payload = serialize_tool_definitions(tools, format=format)
    if tool_payload:
        # The incubating semconv module does not yet expose a constant for this key.
        attrs["gen_ai.tool.definitions"] = tool_payload

    return attrs


def apply_param_attributes(
    attrs: dict[str, AttributeValue], params: ParamsDict
) -> None:
    if not params:
        return

    for key, attr_key in PARAM_ATTRIBUTE_MAP.items():
        if key not in params:
            continue
        value = params[key]
        if value is None:
            continue
        if key in {"stop", "stop_sequences"} and isinstance(value, str):
            value = [value]
        attrs[attr_key] = value


PARAM_ATTRIBUTE_MAP: Mapping[str, str] = {
    "temperature": GenAIAttributes.GEN_AI_REQUEST_TEMPERATURE,
    "max_tokens": GenAIAttributes.GEN_AI_REQUEST_MAX_TOKENS,
    "max_output_tokens": GenAIAttributes.GEN_AI_REQUEST_MAX_TOKENS,
    "max_completion_tokens": GenAIAttributes.GEN_AI_REQUEST_MAX_TOKENS,
    "top_p": GenAIAttributes.GEN_AI_REQUEST_TOP_P,
    "top_k": GenAIAttributes.GEN_AI_REQUEST_TOP_K,
    "frequency_penalty": GenAIAttributes.GEN_AI_REQUEST_FREQUENCY_PENALTY,
    "presence_penalty": GenAIAttributes.GEN_AI_REQUEST_PRESENCE_PENALTY,
    "seed": GenAIAttributes.GEN_AI_REQUEST_SEED,
    "stop_sequences": GenAIAttributes.GEN_AI_REQUEST_STOP_SEQUENCES,
    "stop": GenAIAttributes.GEN_AI_REQUEST_STOP_SEQUENCES,
    "n": GenAIAttributes.GEN_AI_REQUEST_CHOICE_COUNT,
    "choice_count": GenAIAttributes.GEN_AI_REQUEST_CHOICE_COUNT,
}


def infer_output_type(format_obj: FormatParam) -> str:
    if format_obj is None:
        return GenAIAttributes.GenAiOutputTypeValues.TEXT.value
    return GenAIAttributes.GenAiOutputTypeValues.JSON.value


def serialize_tool_definitions(
    tools: ToolsParam,
    format: FormatParam = None,
) -> str | None:
    if tools is None:
        tool_schemas: list[ToolSchema] = []
    else:
        tool_schemas = collect_tool_schemas(tools)

    if isinstance(format, Format) and format.mode == "tool":
        tool_schemas.append(create_tool_schema(format))

    if not tool_schemas:
        return None
    definitions: list[dict[str, str | int | bool | dict[str, str | int | bool]]] = []
    for tool in tool_schemas:
        definitions.append(
            {
                "name": tool.name,
                "description": tool.description,
                "strict": tool.strict,
                "parameters": tool.parameters.model_dump(by_alias=True, mode="json"),
            }
        )
    return json_dumps(definitions)


def collect_tool_schemas(
    tools: Sequence[ToolSchema | type] | BaseToolkit,
) -> list[ToolSchema]:
    iterable = list(tools.tools) if isinstance(tools, BaseToolkit) else list(tools)
    schemas: list[ToolSchema] = []
    for tool in iterable:
        if isinstance(tool, ToolSchema):
            schemas.append(tool)
    return schemas


def extract_response_id(raw: dict[str, str | int] | str | None) -> str | None:
    if isinstance(raw, dict):
        for key in ("id", "response_id", "responseId"):
            value = raw.get(key)
            if isinstance(value, str):
                return value
    return None
