"""Shared utilities and types for OpenTelemetry GenAI instrumentation."""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, TypeAlias, runtime_checkable
from typing_extensions import TypeIs

from opentelemetry import trace as otel_trace
from opentelemetry.semconv._incubating.attributes import (
    gen_ai_attributes as GenAIAttributes,
)
from opentelemetry.semconv.attributes import error_attributes as ErrorAttributes
from opentelemetry.trace import SpanKind, Status, StatusCode

from .....llm import (
    AnyTools,
    AnyToolSchema,
    BaseToolkit,
    Format,
    FormatSpec,
    FormattableT,
    Jsonable,
    Message,
    Model,
    ModelId,
    Params,
    ProviderId,
    ProviderTool,
    RootResponse,
    ToolkitT,
)
from ...configuration import get_tracer
from ...utils import json_dumps
from .cost import calculate_cost_async, calculate_cost_sync
from .encode import (
    map_finish_reason,
    snapshot_from_root_response,
    split_request_messages,
)
from .serialize import (
    serialize_mirascope_content,
    serialize_mirascope_cost,
    serialize_mirascope_messages,
    serialize_mirascope_usage,
    serialize_tools,
)

logger = logging.getLogger(__name__)

# Re-export for backwards compatibility
_calculate_cost_sync = calculate_cost_sync
_calculate_cost_async = calculate_cost_async

if TYPE_CHECKING:
    from opentelemetry.trace import Span, Tracer
    from opentelemetry.util.types import AttributeValue

    from . import gen_ai_types
else:
    AttributeValue = None
    Span = None
    Tracer = None


FormatParam: TypeAlias = FormatSpec[FormattableT] | None
ParamsDict: TypeAlias = Mapping[str, str | int | float | bool | Sequence[str] | None]
SpanAttributes: TypeAlias = Mapping[str, AttributeValue]
AttributeSetter: TypeAlias = Callable[[str, AttributeValue], None]
ParamsValue = str | int | float | bool | Sequence[str] | None


@dataclass(slots=True)
class SpanContext:
    """Container for a GenAI span and its associated dropped parameters."""

    span: Span | None
    """The active span, if any."""

    dropped_params: dict[str, Jsonable]
    """Parameters that could not be recorded as span attributes."""


@runtime_checkable
class Identifiable(Protocol):
    """Protocol for objects with an optional ID attribute."""

    id: str | None
    """Optional ID attribute."""


_PARAM_ATTRIBUTE_MAP: Mapping[str, str] = {
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


def record_exception(span: Span, exc: Exception) -> None:
    """Record exception details on span following OpenTelemetry semantic conventions."""
    span.record_exception(exc)
    span.set_attribute(ErrorAttributes.ERROR_TYPE, exc.__class__.__name__)
    error_message = str(exc)
    if error_message:
        span.set_attribute("error.message", error_message)
    span.set_status(Status(StatusCode.ERROR, error_message))


def _infer_output_type(format_obj: FormatParam) -> str:
    """Infer the GenAI output type from the format parameter."""
    if format_obj is None:
        return GenAIAttributes.GenAiOutputTypeValues.TEXT.value
    return GenAIAttributes.GenAiOutputTypeValues.JSON.value


def _apply_param_attributes(
    attrs: dict[str, AttributeValue], params: ParamsDict
) -> None:
    """Apply model parameters as span attributes."""
    if not params:
        return

    for key, attr_key in _PARAM_ATTRIBUTE_MAP.items():
        if key not in params:
            continue
        value = params[key]
        if value is None:
            continue
        if key in {"stop", "stop_sequences"} and isinstance(value, str):
            value = [value]
        attrs[attr_key] = value


def _set_json_attribute(
    setter: AttributeSetter,
    *,
    key: str,
    payload: (
        gen_ai_types.SystemInstructions
        | gen_ai_types.InputMessages
        | gen_ai_types.OutputMessages
    ),
) -> None:
    """Assign a JSON-serialized attribute to a span."""
    if not payload:
        return
    setter(key, json_dumps(payload))


def _assign_request_message_attributes(
    setter: AttributeSetter,
    *,
    messages: Sequence[Message],
) -> None:
    """Assign request message attributes to a span."""
    system_payload, input_payload = split_request_messages(messages)
    _set_json_attribute(
        setter,
        key=GenAIAttributes.GEN_AI_SYSTEM_INSTRUCTIONS,
        payload=system_payload,
    )
    _set_json_attribute(
        setter,
        key=GenAIAttributes.GEN_AI_INPUT_MESSAGES,
        payload=input_payload,
    )


def _build_request_attributes(
    *,
    operation: str,
    provider: ProviderId,
    model_id: ModelId,
    messages: Sequence[Message],
    tools: AnyTools | None,
    format: FormatParam,
    params: ParamsDict,
) -> dict[str, AttributeValue]:
    """Build GenAI request attributes for a span."""
    attrs: dict[str, AttributeValue] = {
        GenAIAttributes.GEN_AI_OPERATION_NAME: operation,
        GenAIAttributes.GEN_AI_PROVIDER_NAME: provider,
        GenAIAttributes.GEN_AI_REQUEST_MODEL: model_id,
        GenAIAttributes.GEN_AI_OUTPUT_TYPE: _infer_output_type(format),
    }
    _apply_param_attributes(attrs, params)

    _assign_request_message_attributes(
        attrs.__setitem__,
        messages=messages,
    )

    tool_schemas: list[AnyToolSchema | ProviderTool] = []
    if tools is None:
        tool_schemas = []
    elif isinstance(tools, BaseToolkit):
        tool_schemas = list(tools.tools)
    else:
        tool_schemas = list(tools)

    if isinstance(format, Format) and format.mode == "tool":
        tool_schemas.append(format.create_tool_schema())

    tool_payload = serialize_tools(tool_schemas)
    if tool_payload:
        # The incubating semconv module does not yet expose a constant for this key.
        attrs["gen_ai.tool.definitions"] = tool_payload

    return attrs


def _extract_response_id(
    raw: dict[str, str | int] | str | Identifiable | None,
) -> str | None:
    """Extract response ID from raw response data."""
    if isinstance(raw, dict):
        for key in ("id", "response_id", "responseId"):
            value = raw.get(key)
            if isinstance(value, str):
                return value
    elif isinstance(raw, Identifiable):
        return raw.id
    return None


def attach_response(
    span: Span,
    response: RootResponse[ToolkitT, FormattableT | None],
    *,
    request_messages: Sequence[Message],
) -> None:
    """Attach response attributes to a GenAI span."""
    span.set_attribute(GenAIAttributes.GEN_AI_RESPONSE_MODEL, response.model_id)
    span.set_attribute(
        GenAIAttributes.GEN_AI_RESPONSE_FINISH_REASONS,
        [map_finish_reason(response.finish_reason)],
    )
    response_id = _extract_response_id(getattr(response, "raw", None))
    if response_id:
        span.set_attribute(GenAIAttributes.GEN_AI_RESPONSE_ID, response_id)

    snapshot = snapshot_from_root_response(
        response,
        request_messages=request_messages,
    )
    _set_json_attribute(
        span.set_attribute,
        key=GenAIAttributes.GEN_AI_SYSTEM_INSTRUCTIONS,
        payload=snapshot.system_instructions,
    )
    _set_json_attribute(
        span.set_attribute,
        key=GenAIAttributes.GEN_AI_INPUT_MESSAGES,
        payload=snapshot.inputs,
    )
    _set_json_attribute(
        span.set_attribute,
        key=GenAIAttributes.GEN_AI_OUTPUT_MESSAGES,
        payload=snapshot.outputs,
    )
    if response.usage is not None:
        span.set_attribute(
            GenAIAttributes.GEN_AI_USAGE_INPUT_TOKENS, response.usage.input_tokens
        )
        span.set_attribute(
            GenAIAttributes.GEN_AI_USAGE_OUTPUT_TOKENS, response.usage.output_tokens
        )

    # Mirascope-specific attributes
    span.set_attribute(
        "mirascope.response.messages", serialize_mirascope_messages(request_messages)
    )
    span.set_attribute(
        "mirascope.response.content", serialize_mirascope_content(response.content)
    )
    if (usage_json := serialize_mirascope_usage(response.usage)) is not None:
        span.set_attribute("mirascope.response.usage", usage_json)

    # Calculate and attach cost if usage is available
    if response.usage is not None:
        cost = _calculate_cost_sync(
            response.provider_id, response.model_id, response.usage
        )
        if cost is not None:
            span.set_attribute(
                "mirascope.response.cost",
                serialize_mirascope_cost(
                    input_cost=cost.input_cost_centicents,
                    output_cost=cost.output_cost_centicents,
                    total_cost=cost.total_cost_centicents,
                    cache_read_cost=cost.cache_read_cost_centicents,
                    cache_write_cost=cost.cache_write_cost_centicents,
                ),
            )


async def attach_response_async(
    span: Span,
    response: RootResponse[ToolkitT, FormattableT | None],
    *,
    request_messages: Sequence[Message],
) -> None:
    """Attach response attributes to a GenAI span (async version for cost calculation)."""
    span.set_attribute(GenAIAttributes.GEN_AI_RESPONSE_MODEL, response.model_id)
    span.set_attribute(
        GenAIAttributes.GEN_AI_RESPONSE_FINISH_REASONS,
        [map_finish_reason(response.finish_reason)],
    )
    response_id = _extract_response_id(getattr(response, "raw", None))
    if response_id:
        span.set_attribute(GenAIAttributes.GEN_AI_RESPONSE_ID, response_id)

    snapshot = snapshot_from_root_response(
        response,
        request_messages=request_messages,
    )
    _set_json_attribute(
        span.set_attribute,
        key=GenAIAttributes.GEN_AI_SYSTEM_INSTRUCTIONS,
        payload=snapshot.system_instructions,
    )
    _set_json_attribute(
        span.set_attribute,
        key=GenAIAttributes.GEN_AI_INPUT_MESSAGES,
        payload=snapshot.inputs,
    )
    _set_json_attribute(
        span.set_attribute,
        key=GenAIAttributes.GEN_AI_OUTPUT_MESSAGES,
        payload=snapshot.outputs,
    )
    if response.usage is not None:
        span.set_attribute(
            GenAIAttributes.GEN_AI_USAGE_INPUT_TOKENS, response.usage.input_tokens
        )
        span.set_attribute(
            GenAIAttributes.GEN_AI_USAGE_OUTPUT_TOKENS, response.usage.output_tokens
        )

    # Mirascope-specific attributes
    span.set_attribute(
        "mirascope.response.messages", serialize_mirascope_messages(request_messages)
    )
    span.set_attribute(
        "mirascope.response.content", serialize_mirascope_content(response.content)
    )
    if (usage_json := serialize_mirascope_usage(response.usage)) is not None:
        span.set_attribute("mirascope.response.usage", usage_json)

    # Calculate and attach cost if usage is available (async)
    if response.usage is not None:
        cost = await _calculate_cost_async(
            response.provider_id, response.model_id, response.usage
        )
        if cost is not None:
            span.set_attribute(
                "mirascope.response.cost",
                serialize_mirascope_cost(
                    input_cost=cost.input_cost_centicents,
                    output_cost=cost.output_cost_centicents,
                    total_cost=cost.total_cost_centicents,
                    cache_read_cost=cost.cache_read_cost_centicents,
                    cache_write_cost=cost.cache_write_cost_centicents,
                ),
            )


def _is_supported_param_value(value: object) -> TypeIs[ParamsValue]:
    """Returns True if the value can be exported as an OTEL attribute."""
    if isinstance(value, str | int | float | bool) or value is None:
        return True
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        return all(isinstance(item, str) for item in value)
    return False


def _normalize_dropped_value(value: object) -> Jsonable:
    """Returns a JSON-safe representation for unsupported param values."""
    if isinstance(value, str | int | float | bool) or value is None:
        return value
    if isinstance(value, Mapping):
        normalized: dict[str, Jsonable] = {}
        for key, item in value.items():
            normalized[str(key)] = _normalize_dropped_value(item)
        return normalized
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return [_normalize_dropped_value(item) for item in value]
    try:
        return str(value)
    except Exception:  # pragma: no cover
        return f"<{type(value).__name__}>"


def _params_as_mapping(params: Params) -> tuple[ParamsDict, dict[str, Jsonable]]:
    """Returns supported params and a mapping of dropped params."""
    filtered: dict[str, ParamsValue] = {}
    dropped: dict[str, Jsonable] = {}
    for key, value in params.items():
        if _is_supported_param_value(value):
            filtered[key] = value
        else:
            dropped[key] = _normalize_dropped_value(value)
    return filtered, dropped


def record_dropped_params(
    span: Span,
    dropped_params: Mapping[str, Jsonable],
) -> None:
    """Emit an event with JSON-encoded params that cannot become attributes.

    See https://opentelemetry.io/docs/specs/otel/common/ for the attribute type limits,
    https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-events/ for the GenAI
    guidance on recording richer payloads via events, and
    https://opentelemetry.io/blog/2025/complex-attribute-types/ for the recommendation
    to serialize unsupported complex types instead of dropping them outright.
    """
    if not dropped_params:
        return None
    payload = json_dumps(dropped_params)
    span.add_event(
        "gen_ai.request.params.untracked",
        attributes={
            "gen_ai.untracked_params.count": len(dropped_params),
            "gen_ai.untracked_params.keys": list(dropped_params.keys()),
            "gen_ai.untracked_params.json": payload,
        },
    )
    return None


@contextmanager
def start_model_span(
    model: Model,
    *,
    messages: Sequence[Message],
    tools: AnyTools | None,
    format: FormatParam,
    activate: bool = True,
) -> Iterator[SpanContext]:
    """Context manager that yields a SpanContext for a model call."""
    params, dropped_params = _params_as_mapping(model.params)
    tracer = get_tracer()

    if tracer is None or otel_trace is None:
        yield SpanContext(None, dropped_params)
        return

    operation = GenAIAttributes.GenAiOperationNameValues.CHAT.value
    attrs = _build_request_attributes(
        operation=operation,
        provider=model.provider_id,
        model_id=model.model_id,
        messages=messages,
        tools=tools,
        format=format,
        params=params,
    )
    span_name = f"{operation} {model.model_id}"

    if activate:
        with tracer.start_as_current_span(
            name=span_name,
            kind=SpanKind.CLIENT,
        ) as active_span:
            for key, value in attrs.items():
                active_span.set_attribute(key, value)
            try:
                yield SpanContext(active_span, dropped_params)
            except Exception as exc:
                record_exception(active_span, exc)
                raise
        return

    span = tracer.start_span(
        name=span_name,
        kind=SpanKind.CLIENT,
    )
    for key, value in attrs.items():
        span.set_attribute(key, value)
    try:
        yield SpanContext(span, dropped_params)
    except Exception as exc:
        record_exception(span, exc)
        raise
    finally:
        span.end()
