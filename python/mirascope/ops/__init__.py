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
    "SessionContext",
    "Span",
    "TraceDecorator",
    "TracedFunction",
    "TracedResult",
    "current_session",
    "extract_session_id",
    "session",
    "span",
    "trace",
]
