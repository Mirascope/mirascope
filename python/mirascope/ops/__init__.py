"""Operational helpers (tracing, sessions, future ops.* utilities)."""

from __future__ import annotations

from contextlib import suppress

from ._internal.session import (
    SESSION_HEADER_NAME,
    SessionContext,
    current_session,
    extract_session_id,
    session,
)

# TODO: refactor alongside all other import error handling
with suppress(ImportError):
    from ._internal.context import propagated_context
    from ._internal.propagation import (
        ContextPropagator,
        PropagatorFormat,
        extract_context,
        get_propagator,
        inject_context,
        reset_propagator,
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
    "current_session",
    "extract_context",
    "extract_session_id",
    "get_propagator",
    "inject_context",
    "propagated_context",
    "reset_propagator",
    "session",
    "span",
    "trace",
]
