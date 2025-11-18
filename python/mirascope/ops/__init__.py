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

__all__ = [
    "SESSION_HEADER_NAME",
    "SessionContext",
    "Span",
    "current_session",
    "extract_session_id",
    "session",
    "span",
]
