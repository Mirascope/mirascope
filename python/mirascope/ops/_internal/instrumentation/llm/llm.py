"""OpenTelemetry GenAI instrumentation for `mirascope.llm`."""

from __future__ import annotations

import os
import weakref
from collections.abc import AsyncIterator, Callable, Iterator, Mapping, Sequence
from contextlib import AbstractContextManager, contextmanager
from dataclasses import dataclass
from functools import wraps
from types import TracebackType
from typing import TYPE_CHECKING, Protocol, TypeAlias, overload, runtime_checkable
from typing_extensions import TypeIs

from opentelemetry.semconv._incubating.attributes import (
    gen_ai_attributes as GenAIAttributes,
)
from opentelemetry.semconv.attributes import (
    error_attributes as ErrorAttributes,
)

from .....llm.context import Context, DepsT
from .....llm.formatting import Format, FormattableT
from .....llm.formatting._utils import create_tool_schema
from .....llm.messages import Message
from .....llm.models import Model
from .....llm.providers import Params, ProviderId
from .....llm.providers.model_id import ModelId
from .....llm.responses import (
    AsyncContextResponse,
    AsyncContextStreamResponse,
    AsyncResponse,
    ContextResponse,
    ContextStreamResponse,
    Response,
    StreamResponse,
    StreamResponseChunk,
)
from .....llm.responses.root_response import RootResponse
from .....llm.tools import (
    AnyToolFn,
    AnyToolSchema,
    AsyncContextTool,
    AsyncContextToolkit,
    AsyncTool,
    AsyncToolkit,
    ContextTool,
    ContextToolkit,
    Tool,
    Toolkit,
)
from .....llm.tools.tool_schema import ToolSchema
from .....llm.tools.toolkit import BaseToolkit, ToolkitT
from .....llm.types import Jsonable
from ...configuration import (
    get_tracer,
)
from ...utils import json_dumps
from .encode import (
    map_finish_reason,
    snapshot_from_root_response,
    split_request_messages,
)

# TODO: refactor alongside all other import error handling to provide nice error messages
try:
    from opentelemetry import trace as otel_trace
    from opentelemetry.trace import SpanKind, Status, StatusCode
except ImportError:  # pragma: no cover
    if not TYPE_CHECKING:
        otel_trace = None
        SpanKind = None
        StatusCode = None
        Status = None

if TYPE_CHECKING:
    from opentelemetry import trace as otel_trace
    from opentelemetry.trace import (
        Span,
        SpanKind,
        Status,
        StatusCode,
        Tracer,
    )
    from opentelemetry.util.types import AttributeValue

    from . import gen_ai_types
else:
    AttributeValue = None
    Span = None
    Tracer = None


ToolsParam: TypeAlias = (
    Sequence[ToolSchema[AnyToolFn]] | BaseToolkit[AnyToolSchema] | None
)
FormatParam: TypeAlias = Format[FormattableT] | None
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


def _record_exception(span: Span, exc: Exception) -> None:
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


def _collect_tool_schemas(
    tools: Sequence[ToolSchema[AnyToolFn]] | BaseToolkit[AnyToolSchema],
) -> list[ToolSchema[AnyToolFn]]:
    """Collect ToolSchema instances from a tools parameter."""
    iterable = list(tools.tools) if isinstance(tools, BaseToolkit) else list(tools)
    schemas: list[ToolSchema[AnyToolFn]] = []
    for tool in iterable:
        if isinstance(tool, ToolSchema):
            schemas.append(tool)
    return schemas


def _serialize_tool_definitions(
    tools: ToolsParam,
    format: FormatParam = None,
) -> str | None:
    """Serialize tool definitions to JSON for span attributes."""
    if tools is None:
        tool_schemas: list[ToolSchema[AnyToolFn]] = []
    else:
        tool_schemas = _collect_tool_schemas(tools)

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


def _build_request_attributes(
    *,
    operation: str,
    provider: ProviderId,
    model_id: ModelId,
    messages: Sequence[Message],
    tools: ToolsParam,
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

    tool_payload = _serialize_tool_definitions(tools, format=format)
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


def _attach_response(
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
    # TODO: Emit gen_ai.usage metrics once Response exposes provider-agnostic usage fields.


_ORIGINAL_MODEL_CALL = Model.call
_MODEL_CALL_WRAPPED = False
_ORIGINAL_MODEL_CALL_ASYNC = Model.call_async
_MODEL_CALL_ASYNC_WRAPPED = False
_ORIGINAL_MODEL_CONTEXT_CALL = Model.context_call
_MODEL_CONTEXT_CALL_WRAPPED = False
_ORIGINAL_MODEL_CONTEXT_CALL_ASYNC = Model.context_call_async
_MODEL_CONTEXT_CALL_ASYNC_WRAPPED = False
_ORIGINAL_MODEL_STREAM = Model.stream
_MODEL_STREAM_WRAPPED = False
_ORIGINAL_MODEL_CONTEXT_STREAM = Model.context_stream
_MODEL_CONTEXT_STREAM_WRAPPED = False
_ORIGINAL_MODEL_CONTEXT_STREAM_ASYNC = Model.context_stream_async
_MODEL_CONTEXT_STREAM_ASYNC_WRAPPED = False


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


def _record_dropped_params(
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
def _start_model_span(
    model: Model,
    *,
    messages: Sequence[Message],
    tools: ToolsParam,
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
                _record_exception(active_span, exc)
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
        _record_exception(span, exc)
        raise
    finally:
        span.end()


@overload
def _instrumented_model_call(
    self: Model,
    *,
    messages: Sequence[Message],
    tools: Sequence[Tool] | Toolkit | None = None,
    format: None = None,
) -> Response: ...


@overload
def _instrumented_model_call(
    self: Model,
    *,
    messages: Sequence[Message],
    tools: Sequence[Tool] | Toolkit | None = None,
    format: type[FormattableT] | Format[FormattableT],
) -> Response[FormattableT]: ...


@overload
def _instrumented_model_call(
    self: Model,
    *,
    messages: Sequence[Message],
    tools: Sequence[Tool] | Toolkit | None = None,
    format: type[FormattableT] | Format[FormattableT] | None = None,
) -> Response | Response[FormattableT]: ...


@wraps(_ORIGINAL_MODEL_CALL)
def _instrumented_model_call(
    self: Model,
    *,
    messages: Sequence[Message],
    tools: Sequence[Tool] | Toolkit | None = None,
    format: FormatParam = None,
) -> Response | Response[FormattableT]:
    """Returns a GenAI-instrumented result of `Model.call`."""
    with _start_model_span(
        self,
        messages=messages,
        tools=tools,
        format=format,
    ) as span_ctx:
        response = _ORIGINAL_MODEL_CALL(
            self,
            messages=messages,
            tools=tools,
            format=format,
        )
        if span_ctx.span is not None:
            _attach_response(
                span_ctx.span,
                response,
                request_messages=messages,
            )
            _record_dropped_params(span_ctx.span, span_ctx.dropped_params)
        return response


def _wrap_model_call() -> None:
    """Returns None. Replaces `Model.call` with the instrumented wrapper."""
    global _MODEL_CALL_WRAPPED
    if _MODEL_CALL_WRAPPED:
        return
    Model.call = _instrumented_model_call
    _MODEL_CALL_WRAPPED = True


def _unwrap_model_call() -> None:
    """Returns None. Restores the original `Model.call` implementation."""
    global _MODEL_CALL_WRAPPED
    if not _MODEL_CALL_WRAPPED:
        return
    Model.call = _ORIGINAL_MODEL_CALL
    _MODEL_CALL_WRAPPED = False


@overload
async def _instrumented_model_call_async(
    self: Model,
    *,
    messages: Sequence[Message],
    tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
    format: None = None,
) -> AsyncResponse: ...


@overload
async def _instrumented_model_call_async(
    self: Model,
    *,
    messages: Sequence[Message],
    tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
    format: type[FormattableT] | Format[FormattableT],
) -> AsyncResponse[FormattableT]: ...


@overload
async def _instrumented_model_call_async(
    self: Model,
    *,
    messages: Sequence[Message],
    tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
    format: type[FormattableT] | Format[FormattableT] | None = None,
) -> AsyncResponse | AsyncResponse[FormattableT]: ...


@wraps(_ORIGINAL_MODEL_CALL_ASYNC)
async def _instrumented_model_call_async(
    self: Model,
    *,
    messages: Sequence[Message],
    tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
    format: FormatParam = None,
) -> AsyncResponse | AsyncResponse[FormattableT]:
    """Returns a GenAI-instrumented result of `Model.call_async`."""
    with _start_model_span(
        self,
        messages=messages,
        tools=tools,
        format=format,
        activate=True,
    ) as span_ctx:
        response = await _ORIGINAL_MODEL_CALL_ASYNC(
            self,
            messages=messages,
            tools=tools,
            format=format,
        )
        if span_ctx.span is not None:
            _attach_response(
                span_ctx.span,
                response,
                request_messages=messages,
            )
            _record_dropped_params(span_ctx.span, span_ctx.dropped_params)
        return response


def _wrap_model_call_async() -> None:
    """Returns None. Replaces `Model.call_async` with the instrumented wrapper."""
    global _MODEL_CALL_ASYNC_WRAPPED
    if _MODEL_CALL_ASYNC_WRAPPED:
        return
    Model.call_async = _instrumented_model_call_async
    _MODEL_CALL_ASYNC_WRAPPED = True


def _unwrap_model_call_async() -> None:
    """Returns None. Restores the original `Model.call_async` implementation."""
    global _MODEL_CALL_ASYNC_WRAPPED
    if not _MODEL_CALL_ASYNC_WRAPPED:
        return
    Model.call_async = _ORIGINAL_MODEL_CALL_ASYNC
    _MODEL_CALL_ASYNC_WRAPPED = False


@overload
def _instrumented_model_context_call(
    self: Model,
    *,
    ctx: Context[DepsT],
    messages: Sequence[Message],
    tools: Sequence[Tool | ContextTool[DepsT]] | ContextToolkit[DepsT] | None = None,
    format: None = None,
) -> ContextResponse[DepsT, None]: ...


@overload
def _instrumented_model_context_call(
    self: Model,
    *,
    ctx: Context[DepsT],
    messages: Sequence[Message],
    tools: Sequence[Tool | ContextTool[DepsT]] | ContextToolkit[DepsT] | None = None,
    format: type[FormattableT] | Format[FormattableT],
) -> ContextResponse[DepsT, FormattableT]: ...


@overload
def _instrumented_model_context_call(
    self: Model,
    *,
    ctx: Context[DepsT],
    messages: Sequence[Message],
    tools: Sequence[Tool | ContextTool[DepsT]] | ContextToolkit[DepsT] | None = None,
    format: type[FormattableT] | Format[FormattableT] | None = None,
) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]: ...


@wraps(_ORIGINAL_MODEL_CONTEXT_CALL)
def _instrumented_model_context_call(
    self: Model,
    *,
    ctx: Context[DepsT],
    messages: Sequence[Message],
    tools: Sequence[Tool | ContextTool[DepsT]] | ContextToolkit[DepsT] | None = None,
    format: FormatParam = None,
) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
    """Returns a GenAI-instrumented result of `Model.context_call`."""
    with _start_model_span(
        self,
        messages=messages,
        tools=tools,
        format=format,
        activate=True,
    ) as span_ctx:
        response = _ORIGINAL_MODEL_CONTEXT_CALL(
            self,
            ctx=ctx,
            messages=messages,
            tools=tools,
            format=format,
        )
        if span_ctx.span is not None:
            _attach_response(
                span_ctx.span,
                response,
                request_messages=messages,
            )
            _record_dropped_params(span_ctx.span, span_ctx.dropped_params)
        return response


def _wrap_model_context_call() -> None:
    """Returns None. Replaces `Model.context_call` with the instrumented wrapper."""
    global _MODEL_CONTEXT_CALL_WRAPPED
    if _MODEL_CONTEXT_CALL_WRAPPED:
        return
    Model.context_call = _instrumented_model_context_call
    _MODEL_CONTEXT_CALL_WRAPPED = True


def _unwrap_model_context_call() -> None:
    """Returns None. Restores the original `Model.context_call` implementation."""
    global _MODEL_CONTEXT_CALL_WRAPPED
    if not _MODEL_CONTEXT_CALL_WRAPPED:
        return
    Model.context_call = _ORIGINAL_MODEL_CONTEXT_CALL
    _MODEL_CONTEXT_CALL_WRAPPED = False


@overload
async def _instrumented_model_context_call_async(
    self: Model,
    *,
    ctx: Context[DepsT],
    messages: Sequence[Message],
    tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
    | AsyncContextToolkit[DepsT]
    | None = None,
    format: None = None,
) -> AsyncContextResponse[DepsT, None]: ...


@overload
async def _instrumented_model_context_call_async(
    self: Model,
    *,
    ctx: Context[DepsT],
    messages: Sequence[Message],
    tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
    | AsyncContextToolkit[DepsT]
    | None = None,
    format: type[FormattableT] | Format[FormattableT],
) -> AsyncContextResponse[DepsT, FormattableT]: ...


@overload
async def _instrumented_model_context_call_async(
    self: Model,
    *,
    ctx: Context[DepsT],
    messages: Sequence[Message],
    tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
    | AsyncContextToolkit[DepsT]
    | None = None,
    format: type[FormattableT] | Format[FormattableT] | None = None,
) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]: ...


@wraps(_ORIGINAL_MODEL_CONTEXT_CALL_ASYNC)
async def _instrumented_model_context_call_async(
    self: Model,
    *,
    ctx: Context[DepsT],
    messages: Sequence[Message],
    tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
    | AsyncContextToolkit[DepsT]
    | None = None,
    format: FormatParam = None,
) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
    """Returns a GenAI-instrumented result of `Model.context_call_async`."""
    with _start_model_span(
        self,
        messages=messages,
        tools=tools,
        format=format,
        activate=True,
    ) as span_ctx:
        response = await _ORIGINAL_MODEL_CONTEXT_CALL_ASYNC(
            self,
            ctx=ctx,
            messages=messages,
            tools=tools,
            format=format,
        )
        if span_ctx.span is not None:
            _attach_response(
                span_ctx.span,
                response,
                request_messages=messages,
            )
            _record_dropped_params(span_ctx.span, span_ctx.dropped_params)
        return response


def _wrap_model_context_call_async() -> None:
    """Returns None. Replaces `Model.context_call_async` with the instrumented wrapper."""
    global _MODEL_CONTEXT_CALL_ASYNC_WRAPPED
    if _MODEL_CONTEXT_CALL_ASYNC_WRAPPED:
        return
    Model.context_call_async = _instrumented_model_context_call_async
    _MODEL_CONTEXT_CALL_ASYNC_WRAPPED = True


def _unwrap_model_context_call_async() -> None:
    """Returns None. Restores the original `Model.context_call_async` implementation."""
    global _MODEL_CONTEXT_CALL_ASYNC_WRAPPED
    if not _MODEL_CONTEXT_CALL_ASYNC_WRAPPED:
        return
    Model.context_call_async = _ORIGINAL_MODEL_CONTEXT_CALL_ASYNC
    _MODEL_CONTEXT_CALL_ASYNC_WRAPPED = False


@overload
def _instrumented_model_stream(
    self: Model,
    *,
    messages: Sequence[Message],
    tools: Sequence[Tool] | Toolkit | None = None,
    format: None = None,
) -> StreamResponse: ...


@overload
def _instrumented_model_stream(
    self: Model,
    *,
    messages: Sequence[Message],
    tools: Sequence[Tool] | Toolkit | None = None,
    format: type[FormattableT] | Format[FormattableT],
) -> StreamResponse[FormattableT]: ...


@overload
def _instrumented_model_stream(
    self: Model,
    *,
    messages: Sequence[Message],
    tools: Sequence[Tool] | Toolkit | None = None,
    format: type[FormattableT] | Format[FormattableT] | None = None,
) -> StreamResponse | StreamResponse[FormattableT]: ...


@wraps(_ORIGINAL_MODEL_STREAM)
def _instrumented_model_stream(
    self: Model,
    *,
    messages: Sequence[Message],
    tools: Sequence[Tool] | Toolkit | None = None,
    format: FormatParam = None,
) -> StreamResponse | StreamResponse[FormattableT]:
    """Returns a GenAI-instrumented result of `Model.stream`."""
    span_cm = _start_model_span(
        self,
        messages=messages,
        tools=tools,
        format=format,
        activate=False,
    )
    span_ctx = span_cm.__enter__()
    if span_ctx.span is None:
        response = _ORIGINAL_MODEL_STREAM(
            self,
            messages=messages,
            tools=tools,
            format=format,
        )
        span_cm.__exit__(None, None, None)
        return response

    try:
        with otel_trace.use_span(span_ctx.span, end_on_exit=False):
            response = _ORIGINAL_MODEL_STREAM(
                self,
                messages=messages,
                tools=tools,
                format=format,
            )
    except Exception as exc:
        span_cm.__exit__(type(exc), exc, exc.__traceback__)
        raise

    _record_dropped_params(span_ctx.span, span_ctx.dropped_params)

    try:
        _attach_stream_span_handlers(
            response=response,
            span_cm=span_cm,
            span=span_ctx.span,
            request_messages=messages,
        )
    except Exception as exc:  # pragma: no cover
        span_cm.__exit__(type(exc), exc, exc.__traceback__)
        raise

    return response


def _attach_stream_span_handlers(
    *,
    response: ContextStreamResponse[DepsT, FormattableT | None]
    | StreamResponse[FormattableT | None],
    span_cm: AbstractContextManager[SpanContext],
    span: Span,
    request_messages: Sequence[Message],
) -> None:
    """Returns None. Closes the span when streaming completes."""
    chunk_iterator: Iterator[StreamResponseChunk] = response._chunk_iterator

    response_ref = weakref.ref(response)
    closed = False

    def _close_span(
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        nonlocal closed
        if closed:
            return
        closed = True
        response_obj = response_ref()
        if response_obj is not None:
            _attach_response(
                span,
                response_obj,
                request_messages=request_messages,
            )
        span_cm.__exit__(exc_type, exc, tb)

    def _wrapped_iterator() -> Iterator[StreamResponseChunk]:
        with otel_trace.use_span(span, end_on_exit=False):
            try:
                yield from chunk_iterator
            except Exception as exc:  # noqa: BLE001
                _close_span(type(exc), exc, exc.__traceback__)
                raise
            else:
                _close_span(None, None, None)
            finally:
                _close_span(None, None, None)

    response._chunk_iterator = _wrapped_iterator()


def _wrap_model_stream() -> None:
    """Returns None. Replaces `Model.stream` with the instrumented wrapper."""
    global _MODEL_STREAM_WRAPPED
    if _MODEL_STREAM_WRAPPED:
        return
    Model.stream = _instrumented_model_stream
    _MODEL_STREAM_WRAPPED = True


def _unwrap_model_stream() -> None:
    """Returns None. Restores the original `Model.stream` implementation."""
    global _MODEL_STREAM_WRAPPED
    if not _MODEL_STREAM_WRAPPED:
        return
    Model.stream = _ORIGINAL_MODEL_STREAM
    _MODEL_STREAM_WRAPPED = False


@overload
def _instrumented_model_context_stream(
    self: Model,
    *,
    ctx: Context[DepsT],
    messages: Sequence[Message],
    tools: Sequence[Tool | ContextTool[DepsT]] | ContextToolkit[DepsT] | None = None,
    format: None = None,
) -> ContextStreamResponse[DepsT, None]: ...


@overload
def _instrumented_model_context_stream(
    self: Model,
    *,
    ctx: Context[DepsT],
    messages: Sequence[Message],
    tools: Sequence[Tool | ContextTool[DepsT]] | ContextToolkit[DepsT] | None = None,
    format: type[FormattableT] | Format[FormattableT],
) -> ContextStreamResponse[DepsT, FormattableT]: ...


@overload
def _instrumented_model_context_stream(
    self: Model,
    *,
    ctx: Context[DepsT],
    messages: Sequence[Message],
    tools: Sequence[Tool | ContextTool[DepsT]] | ContextToolkit[DepsT] | None = None,
    format: type[FormattableT] | Format[FormattableT] | None = None,
) -> (
    ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]
): ...


@wraps(_ORIGINAL_MODEL_CONTEXT_STREAM)
def _instrumented_model_context_stream(
    self: Model,
    *,
    ctx: Context[DepsT],
    messages: Sequence[Message],
    tools: Sequence[Tool | ContextTool[DepsT]] | ContextToolkit[DepsT] | None = None,
    format: FormatParam = None,
) -> ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]:
    """Returns a GenAI-instrumented result of `Model.context_stream`."""
    span_cm = _start_model_span(
        self,
        messages=messages,
        tools=tools,
        format=format,
        activate=False,
    )
    span_ctx = span_cm.__enter__()
    if span_ctx.span is None:
        response = _ORIGINAL_MODEL_CONTEXT_STREAM(
            self,
            ctx=ctx,
            messages=messages,
            tools=tools,
            format=format,
        )
        span_cm.__exit__(None, None, None)
        return response

    try:
        with otel_trace.use_span(span_ctx.span, end_on_exit=False):
            response = _ORIGINAL_MODEL_CONTEXT_STREAM(
                self,
                ctx=ctx,
                messages=messages,
                tools=tools,
                format=format,
            )
    except Exception as exc:
        span_cm.__exit__(type(exc), exc, exc.__traceback__)
        raise

    _record_dropped_params(span_ctx.span, span_ctx.dropped_params)

    try:
        _attach_stream_span_handlers(
            response=response,
            span_cm=span_cm,
            span=span_ctx.span,
            request_messages=messages,
        )
    except Exception as exc:  # pragma: no cover
        span_cm.__exit__(type(exc), exc, exc.__traceback__)
        raise

    return response


def _wrap_model_context_stream() -> None:
    """Returns None. Replaces `Model.context_stream` with the instrumented wrapper."""
    global _MODEL_CONTEXT_STREAM_WRAPPED
    if _MODEL_CONTEXT_STREAM_WRAPPED:
        return
    Model.context_stream = _instrumented_model_context_stream
    _MODEL_CONTEXT_STREAM_WRAPPED = True


def _unwrap_model_context_stream() -> None:
    """Returns None. Restores the original `Model.context_stream` implementation."""
    global _MODEL_CONTEXT_STREAM_WRAPPED
    if not _MODEL_CONTEXT_STREAM_WRAPPED:
        return
    Model.context_stream = _ORIGINAL_MODEL_CONTEXT_STREAM
    _MODEL_CONTEXT_STREAM_WRAPPED = False


def _attach_async_stream_span_handlers(
    *,
    response: AsyncContextStreamResponse[DepsT, FormattableT | None],
    span_cm: AbstractContextManager[SpanContext],
    span: Span,
    request_messages: Sequence[Message],
) -> None:
    """Returns None. Closes the span when async streaming completes."""
    chunk_iterator: AsyncIterator[StreamResponseChunk] = response._chunk_iterator

    response_ref = weakref.ref(response)
    closed = False

    def _close_span(
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        nonlocal closed
        if closed:
            return
        closed = True
        response_obj = response_ref()
        if response_obj is not None:
            _attach_response(
                span,
                response_obj,
                request_messages=request_messages,
            )
        span_cm.__exit__(exc_type, exc, tb)

    async def _wrapped_iterator() -> AsyncIterator[StreamResponseChunk]:
        try:
            async for chunk in chunk_iterator:
                yield chunk
        except Exception as exc:  # noqa: BLE001
            _close_span(type(exc), exc, exc.__traceback__)
            raise
        else:
            _close_span(None, None, None)
        finally:
            _close_span(None, None, None)

    response._chunk_iterator = _wrapped_iterator()


@overload
async def _instrumented_model_context_stream_async(
    self: Model,
    *,
    ctx: Context[DepsT],
    messages: Sequence[Message],
    tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
    | AsyncContextToolkit[DepsT]
    | None = None,
    format: None = None,
) -> AsyncContextStreamResponse[DepsT, None]: ...


@overload
async def _instrumented_model_context_stream_async(
    self: Model,
    *,
    ctx: Context[DepsT],
    messages: Sequence[Message],
    tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
    | AsyncContextToolkit[DepsT]
    | None = None,
    format: type[FormattableT] | Format[FormattableT],
) -> AsyncContextStreamResponse[DepsT, FormattableT]: ...


@overload
async def _instrumented_model_context_stream_async(
    self: Model,
    *,
    ctx: Context[DepsT],
    messages: Sequence[Message],
    tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
    | AsyncContextToolkit[DepsT]
    | None = None,
    format: type[FormattableT] | Format[FormattableT] | None = None,
) -> (
    AsyncContextStreamResponse[DepsT, None]
    | AsyncContextStreamResponse[DepsT, FormattableT]
): ...


@wraps(_ORIGINAL_MODEL_CONTEXT_STREAM_ASYNC)
async def _instrumented_model_context_stream_async(
    self: Model,
    *,
    ctx: Context[DepsT],
    messages: Sequence[Message],
    tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
    | AsyncContextToolkit[DepsT]
    | None = None,
    format: FormatParam = None,
) -> (
    AsyncContextStreamResponse[DepsT, None]
    | AsyncContextStreamResponse[DepsT, FormattableT]
):
    """Returns a GenAI-instrumented result of `Model.context_stream_async`."""
    span_cm = _start_model_span(
        self,
        messages=messages,
        tools=tools,
        format=format,
        activate=False,
    )
    span_ctx = span_cm.__enter__()
    if span_ctx.span is None:
        response = await _ORIGINAL_MODEL_CONTEXT_STREAM_ASYNC(
            self,
            ctx=ctx,
            messages=messages,
            tools=tools,
            format=format,
        )
        span_cm.__exit__(None, None, None)
        return response

    try:
        with otel_trace.use_span(span_ctx.span, end_on_exit=False):
            response = await _ORIGINAL_MODEL_CONTEXT_STREAM_ASYNC(
                self,
                ctx=ctx,
                messages=messages,
                tools=tools,
                format=format,
            )
    except Exception as exc:
        span_cm.__exit__(type(exc), exc, exc.__traceback__)
        raise

    _record_dropped_params(span_ctx.span, span_ctx.dropped_params)

    try:
        _attach_async_stream_span_handlers(
            response=response,
            span_cm=span_cm,
            span=span_ctx.span,
            request_messages=messages,
        )
    except Exception as exc:  # pragma: no cover
        span_cm.__exit__(type(exc), exc, exc.__traceback__)
        raise

    return response


def _wrap_model_context_stream_async() -> None:
    """Returns None. Replaces `Model.context_stream_async` with the instrumented wrapper."""
    global _MODEL_CONTEXT_STREAM_ASYNC_WRAPPED
    if _MODEL_CONTEXT_STREAM_ASYNC_WRAPPED:
        return
    Model.context_stream_async = _instrumented_model_context_stream_async
    _MODEL_CONTEXT_STREAM_ASYNC_WRAPPED = True


def _unwrap_model_context_stream_async() -> None:
    """Returns None. Restores the original `Model.context_stream_async` implementation."""
    global _MODEL_CONTEXT_STREAM_ASYNC_WRAPPED
    if not _MODEL_CONTEXT_STREAM_ASYNC_WRAPPED:
        return
    Model.context_stream_async = _ORIGINAL_MODEL_CONTEXT_STREAM_ASYNC
    _MODEL_CONTEXT_STREAM_ASYNC_WRAPPED = False


def instrument_llm() -> None:
    """Enable GenAI 1.38 span emission for future `llm.Model` calls and streams.

    Uses the tracer provider configured via `ops.configure()`. If no provider
    was configured, uses the global OpenTelemetry tracer provider.

    Example:

        Enable instrumentation with a custom provider:
        ```python
        from mirascope import ops
        from opentelemetry.sdk.trace import TracerProvider

        provider = TracerProvider()
        ops.configure(tracer_provider=provider)
        ops.instrument_llm()
        ```
    """
    if otel_trace is None:  # pragma: no cover
        raise ImportError(
            "OpenTelemetry is not installed. Run `pip install mirascope[otel]` "
            "and ensure `opentelemetry-api` is available before calling "
            "`instrument_llm`."
        )

    os.environ.setdefault("OTEL_SEMCONV_STABILITY_OPT_IN", "gen_ai_latest_experimental")

    if get_tracer() is None:  # pragma: no cover
        raise RuntimeError(
            "You must call `configure()` before calling `instrument_llm()`."
        )

    _wrap_model_call()
    _wrap_model_call_async()
    _wrap_model_context_call()
    _wrap_model_context_call_async()
    _wrap_model_stream()
    _wrap_model_context_stream()
    _wrap_model_context_stream_async()


def uninstrument_llm() -> None:
    """Disable previously configured instrumentation."""
    _unwrap_model_call()
    _unwrap_model_call_async()
    _unwrap_model_context_call()
    _unwrap_model_context_call_async()
    _unwrap_model_stream()
    _unwrap_model_context_stream()
    _unwrap_model_context_stream_async()
