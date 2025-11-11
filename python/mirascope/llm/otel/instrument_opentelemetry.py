"""Public OpenTelemetry instrumentation API for `mirascope.llm`."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from functools import wraps
from typing import TYPE_CHECKING, Any, overload
from typing_extensions import TypeIs

from opentelemetry.semconv._incubating.attributes import (
    gen_ai_attributes as GenAIAttributes,
)

from ..clients import Params
from ..formatting import Format, FormattableT
from ..messages import Message
from ..models import Model
from ..responses import Response
from ..tools import Tool, Toolkit
from ._json import json_dumps
from ._span import (
    FormatParam,
    ParamsDict,
    attach_response,
    get_tracer,
    set_tracer,
    span as _span,
)

try:
    from opentelemetry import trace as otel_trace
except ImportError:  # pragma: no cover
    otel_trace = None

if TYPE_CHECKING:
    from opentelemetry import trace as otel_trace
    from opentelemetry.trace import Span, TracerProvider


DEFAULT_TRACER_NAME = "mirascope.llm"

ParamsValue = str | int | float | bool | Sequence[str] | None

_ORIGINAL_MODEL_CALL = Model.call
_MODEL_CALL_WRAPPED = False


def _is_supported_param_value(value: object) -> TypeIs[ParamsValue]:
    if isinstance(value, str | int | float | bool) or value is None:
        return True
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        return all(isinstance(item, str) for item in value)
    return False


def _params_as_mapping(params: Params) -> tuple[ParamsDict, dict[str, Any]]:
    filtered: dict[str, ParamsValue] = {}
    dropped: dict[str, object] = {}
    for key, value in params.items():
        if _is_supported_param_value(value):
            filtered[key] = value
        else:
            dropped[key] = value
    return filtered, dropped


def _record_dropped_params(
    span: Span,
    dropped_params: Mapping[str, Any],
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
    try:
        payload = json_dumps(dropped_params)
    except TypeError:
        safe_params: dict[str, str] = {}
        for key, value in dropped_params.items():
            try:
                safe_params[key] = str(value)
            except Exception:
                safe_params[key] = f"<{type(value).__name__}>"
        payload = json_dumps(safe_params)
    span.add_event(
        "gen_ai.request.params.untracked",
        attributes={
            "gen_ai.untracked_params.count": len(dropped_params),
            "gen_ai.untracked_params.keys": list(dropped_params.keys()),
            "gen_ai.untracked_params.json": payload,
        },
    )
    return None


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
    params, dropped_params = _params_as_mapping(self.params)
    operation = GenAIAttributes.GenAiOperationNameValues.CHAT.value
    with _span(
        operation=operation,
        provider=self.provider,
        model_id=self.model_id,
        messages=messages,
        tools=tools,
        format=format,
        params=params,
    ) as span:
        response = _ORIGINAL_MODEL_CALL(
            self,
            messages=messages,
            tools=tools,
            format=format,
        )
        if span is not None:
            attach_response(
                span,
                response,
                request_messages=messages,
            )
            _record_dropped_params(span, dropped_params)
        return response


def _wrap_model_call() -> None:
    global _MODEL_CALL_WRAPPED
    if _MODEL_CALL_WRAPPED:
        return
    Model.call = _instrumented_model_call
    _MODEL_CALL_WRAPPED = True


def _unwrap_model_call() -> None:
    global _MODEL_CALL_WRAPPED
    if not _MODEL_CALL_WRAPPED:
        return
    Model.call = _ORIGINAL_MODEL_CALL
    _MODEL_CALL_WRAPPED = False


def instrument_opentelemetry(
    *,
    tracer_provider: TracerProvider | None = None,
    tracer_name: str = DEFAULT_TRACER_NAME,
    tracer_version: str | None = None,
) -> None:
    """Enable GenAI 1.38 span emission for future `llm.Model` calls."""

    if otel_trace is None:  # pragma: no cover
        raise ImportError(
            "OpenTelemetry is not installed. Run `pip install mirascope[otel]` "
            "and ensure `opentelemetry-api` is available before calling "
            "`instrument_opentelemetry`."
        )

    provider = tracer_provider or otel_trace.get_tracer_provider()
    tracer = provider.get_tracer(tracer_name, tracer_version)
    _wrap_model_call()
    set_tracer(tracer)


def uninstrument_opentelemetry() -> None:
    """Disable previously configured instrumentation."""

    set_tracer(None)
    _unwrap_model_call()


def is_instrumented() -> bool:
    """Return True when OpenTelemetry instrumentation is active."""
    return get_tracer() is not None and _MODEL_CALL_WRAPPED
