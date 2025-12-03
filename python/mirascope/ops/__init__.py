"""Operational helpers (tracing, sessions, future ops.* utilities)."""

from __future__ import annotations

try:
    from ._internal.configuration import configure, tracer_context
    from ._internal.context import propagated_context
    from ._internal.instrumentation.llm import (
        instrument_llm,
        uninstrument_llm,
    )
    from ._internal.propagation import (
        ContextPropagator,
        PropagatorFormat,
        extract_context,
        get_propagator,
        inject_context,
        reset_propagator,
    )
    from ._internal.session import (
        SESSION_HEADER_NAME,
        SessionContext,
        current_session,
        extract_session_id,
        session,
    )
    from ._internal.spans import Span, span
    from ._internal.tracing import (
        AsyncTracedFunction,
        AsyncTracedResult,
        TraceDecorator,
        TracedFunction,
        TracedResult,
        trace,
    )
except ImportError:  # pragma: no cover
    # TODO: refactor alongside other import error handling improvements
    from collections.abc import Callable

    def _create_otel_import_error_stub(name: str) -> Callable[..., None]:
        """Create a stub that raises ImportError with helpful message."""

        def _raise_not_installed() -> None:
            raise ImportError(
                f"The 'opentelemetry' packages are required to use {name}. "
                "Install them with: `uv add 'mirascope[otel]'`."
            )

        return _raise_not_installed

    propagated_context = _create_otel_import_error_stub("propagated_context")
    instrument_llm = _create_otel_import_error_stub("instrument_llm")
    uninstrument_llm = _create_otel_import_error_stub("uninstrument_llm")
    ContextPropagator = _create_otel_import_error_stub("ContextPropagator")
    PropagatorFormat = str
    extract_context = _create_otel_import_error_stub("extract_context")
    get_propagator = _create_otel_import_error_stub("get_propagator")
    inject_context = _create_otel_import_error_stub("inject_context")
    reset_propagator = _create_otel_import_error_stub("reset_propagator")
    SESSION_HEADER_NAME = "X-Mirascope-Session-ID"
    SessionContext = _create_otel_import_error_stub("SessionContext")
    current_session = _create_otel_import_error_stub("current_session")
    extract_session_id = _create_otel_import_error_stub("extract_session_id")
    session = _create_otel_import_error_stub("session")
    Span = _create_otel_import_error_stub("Span")
    span = _create_otel_import_error_stub("span")
    AsyncTracedFunction = _create_otel_import_error_stub("AsyncTracedFunction")
    AsyncTracedResult = _create_otel_import_error_stub("AsyncTracedResult")
    TraceDecorator = _create_otel_import_error_stub("TraceDecorator")
    TracedFunction = _create_otel_import_error_stub("TracedFunction")
    TracedResult = _create_otel_import_error_stub("TracedResult")
    trace = _create_otel_import_error_stub("trace")
    configure = _create_otel_import_error_stub("configure")
    tracer_context = _create_otel_import_error_stub("tracer_context")

__all__ = [
    "SESSION_HEADER_NAME",
    "AsyncTracedFunction",
    "AsyncTracedResult",
    "ContextPropagator",
    "PropagatorFormat",
    "SessionContext",
    "Span",
    "TraceDecorator",
    "TracedFunction",
    "TracedResult",
    "configure",
    "current_session",
    "extract_context",
    "extract_session_id",
    "get_propagator",
    "inject_context",
    "instrument_llm",
    "propagated_context",
    "reset_propagator",
    "session",
    "span",
    "trace",
    "tracer_context",
    "uninstrument_llm",
]
