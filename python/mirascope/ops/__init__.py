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
    from ._internal.traced_calls import (
        TracedAsyncCall,
        TracedAsyncContextCall,
        TracedCall,
        TracedContextCall,
    )
    from ._internal.traced_functions import (
        AsyncTrace,
        AsyncTracedFunction,
        Trace,
        TracedFunction,
    )
    from ._internal.tracing import (
        TraceDecorator,
        trace,
    )
    from ._internal.versioned_calls import (
        VersionedAsyncCall,
        VersionedAsyncContextCall,
        VersionedCall,
        VersionedContextCall,
    )
    from ._internal.versioned_functions import (
        AsyncVersionedFunction,
        VersionedFunction,
        VersionInfo,
    )
    from ._internal.versioning import (
        VersionDecorator,
        version,
    )
    from .exceptions import ClosureComputationError

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
    AsyncTrace = _create_otel_import_error_stub("AsyncTrace")
    AsyncTracedFunction = _create_otel_import_error_stub("AsyncTracedFunction")
    Trace = _create_otel_import_error_stub("Trace")
    TraceDecorator = _create_otel_import_error_stub("TraceDecorator")
    TracedAsyncCall = _create_otel_import_error_stub("TracedAsyncCall")
    TracedAsyncContextCall = _create_otel_import_error_stub("TracedAsyncContextCall")
    TracedCall = _create_otel_import_error_stub("TracedCall")
    TracedContextCall = _create_otel_import_error_stub("TracedContextCall")
    TracedFunction = _create_otel_import_error_stub("TracedFunction")
    trace = _create_otel_import_error_stub("trace")
    configure = _create_otel_import_error_stub("configure")
    tracer_context = _create_otel_import_error_stub("tracer_context")
    AsyncVersionedFunction = _create_otel_import_error_stub("AsyncVersionedFunction")
    VersionDecorator = _create_otel_import_error_stub("VersionDecorator")
    VersionedAsyncCall = _create_otel_import_error_stub("VersionedAsyncCall")
    VersionedAsyncContextCall = _create_otel_import_error_stub(
        "VersionedAsyncContextCall"
    )
    VersionedCall = _create_otel_import_error_stub("VersionedCall")
    VersionedContextCall = _create_otel_import_error_stub("VersionedContextCall")
    VersionedFunction = _create_otel_import_error_stub("VersionedFunction")
    VersionInfo = _create_otel_import_error_stub("VersionInfo")
    version = _create_otel_import_error_stub("version")


__all__ = [
    "SESSION_HEADER_NAME",
    "AsyncTrace",
    "AsyncTracedFunction",
    "AsyncVersionedFunction",
    "ClosureComputationError",
    "ContextPropagator",
    "PropagatorFormat",
    "SessionContext",
    "Span",
    "Trace",
    "TraceDecorator",
    "TracedAsyncCall",
    "TracedAsyncContextCall",
    "TracedCall",
    "TracedContextCall",
    "TracedFunction",
    "VersionDecorator",
    "VersionInfo",
    "VersionedAsyncCall",
    "VersionedAsyncContextCall",
    "VersionedCall",
    "VersionedContextCall",
    "VersionedFunction",
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
    "version",
]
