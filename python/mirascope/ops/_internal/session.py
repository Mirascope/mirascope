"""Session context helpers for grouping traces."""

from __future__ import annotations

import uuid
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from contextvars import ContextVar, Token
from dataclasses import dataclass, field

from mirascope.ops._internal.types import Jsonable

SESSION_HEADER_NAME = "Mirascope-Session-Id"


SESSION_CONTEXT: ContextVar[SessionContext | None] = ContextVar(
    "MIRASCOPE_SESSION_CONTEXT", default=None
)


@dataclass(slots=True)
class SessionContext:
    """Represents a session context for grouping related spans."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    """Unique identifier for the session. Auto-generated if not provided."""

    attributes: Mapping[str, Jsonable] | None = None
    """Optional JSON-serializable metadata associated with the session."""


@contextmanager
def session(
    *, id: str | None = None, attributes: Mapping[str, Jsonable] | None = None
) -> Iterator[SessionContext]:
    """Context manager for setting session context.

    Sessions are used to group related traces together. The session ID and
    optional attributes are automatically propagated to all spans created
    within the session context and are included in outgoing HTTP requests.

    Args:
        id: Unique identifier for the session. If not provided, a UUID will be
            automatically generated.
        attributes: Optional dictionary of JSON-serializable attributes to
            attach to the session.

    Example:
        ```python
        # With explicit ID
        with mirascope.ops.session(id="user-123") as ctx:
            print(ctx.id)  # "user-123"
            result = requests.get("https://api.example.com")

        # With auto-generated ID
        with mirascope.ops.session() as ctx:
            print(ctx.id)  # Auto-generated UUID
            result = requests.get("https://api.example.com")

        # Nested sessions override parent session
        with mirascope.ops.session(id="1"):
            # Session ID: 1
            with mirascope.ops.session(id="2"):
                # Session ID: 2
            # Session ID: 1
        ```
    """
    if id is not None:
        session_ctx = SessionContext(id=id, attributes=attributes)
    else:
        session_ctx = SessionContext(attributes=attributes)
    token: Token[SessionContext | None] = SESSION_CONTEXT.set(session_ctx)
    try:
        yield session_ctx
    finally:
        SESSION_CONTEXT.reset(token)


def current_session() -> SessionContext | None:
    """Get the current session context if one is active.

    Returns:
        The active SessionContext or None if no session is active.

    Example:
        ```python
        with mirascope.ops.session(id="user-123"):
            ctx = mirascope.ops.current_session()
            print(ctx.id)  # "user-123"

        ctx = mirascope.ops.current_session()
        print(ctx)  # None
        ```
    """
    return SESSION_CONTEXT.get()


def extract_session_id(headers: Mapping[str, str | list[str]]) -> str | None:
    """Extract session ID from carrier headers.

    Performs case-insensitive header name matching and handles both string
    and list[str] header values.

    Args:
        headers: Dictionary of HTTP headers or similar carrier data.

    Returns:
        The extracted session ID or None if not present.

    Example:
        ```python
        headers = {"mirascope-session-id": "session-123"}
        session_id = extract_session_id(headers)
        print(session_id)  # "session-123"
        ```
    """
    normalized_headers = {key.lower(): value for key, value in headers.items()}
    header_name_lower = SESSION_HEADER_NAME.lower()

    if header_name_lower not in normalized_headers:
        return None

    value = normalized_headers[header_name_lower]

    if isinstance(value, list):
        if len(value) > 0:
            return value[0]
        return None

    return value if value else None


__all__ = [
    "SESSION_HEADER_NAME",
    "SessionContext",
    "current_session",
    "extract_session_id",
    "session",
]
