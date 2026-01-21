"""Tests for session context management."""

from __future__ import annotations

import asyncio
from contextlib import suppress

import pytest

import mirascope
from mirascope.ops import SessionContext, extract_session_id
from mirascope.ops._internal.types import Jsonable


def test_session_context_creation() -> None:
    """Create SessionContext with valid parameters."""
    ctx = SessionContext(id="session-123")

    assert ctx.id == "session-123"
    assert ctx.attributes is None


def test_session_context_with_attributes() -> None:
    """Create SessionContext with attributes."""
    attrs = {"user": "alice", "role": "admin"}
    ctx = SessionContext(id="session-456", attributes=attrs)

    assert ctx.id == "session-456"
    assert ctx.attributes == attrs


def test_session_context_auto_generates_id() -> None:
    """Auto-generate session ID when not provided."""
    ctx = SessionContext()
    assert ctx.id is not None
    assert isinstance(ctx.id, str)
    assert len(ctx.id) > 0

    ctx2 = SessionContext()
    assert ctx2.id != ctx.id


def test_session_context_manager() -> None:
    """Set and restore session context."""
    with mirascope.ops.session(id="session-1"):
        ctx = mirascope.ops.current_session()
        assert ctx is not None
        assert ctx.id == "session-1"


def test_session_auto_generates_id() -> None:
    """Auto-generate session ID when not provided to context manager."""
    with mirascope.ops.session():
        ctx = mirascope.ops.current_session()
        assert ctx is not None
        assert ctx.id is not None
        assert isinstance(ctx.id, str)
        assert len(ctx.id) > 0


def test_session_nested() -> None:
    """Handle nested session contexts correctly."""
    with mirascope.ops.session(id="outer"):
        ctx = mirascope.ops.current_session()
        assert ctx is not None
        assert ctx.id == "outer"

        with mirascope.ops.session(id="inner"):
            ctx = mirascope.ops.current_session()
            assert ctx is not None
            assert ctx.id == "inner"

        ctx = mirascope.ops.current_session()
        assert ctx is not None
        assert ctx.id == "outer"


def test_session_exception_unwinding() -> None:
    """Restore session context after exception."""
    with suppress(ValueError), mirascope.ops.session(id="test-session"):
        assert mirascope.ops.current_session() is not None
        raise ValueError("test error")


def test_session_nested_exception() -> None:
    """Restore outer session after exception in inner session."""
    with mirascope.ops.session(id="outer"):
        with suppress(RuntimeError), mirascope.ops.session(id="inner"):
            ctx = mirascope.ops.current_session()
            assert ctx is not None
            assert ctx.id == "inner"
            raise RuntimeError("inner error")

        ctx = mirascope.ops.current_session()
        assert ctx is not None
        assert ctx.id == "outer"


@pytest.mark.asyncio
async def test_session_async_propagation() -> None:
    """Propagate session context across async boundaries."""

    async def inner_task() -> str | None:
        await asyncio.sleep(0.001)
        ctx = mirascope.ops.current_session()
        return ctx.id if ctx else None

    with mirascope.ops.session(id="async-session"):
        result = await inner_task()
        assert result == "async-session"


@pytest.mark.asyncio
async def test_session_async_nested() -> None:
    """Handle nested sessions in async context."""

    async def task_with_override() -> str | None:
        with mirascope.ops.session(id="override"):
            await asyncio.sleep(0.001)
            ctx = mirascope.ops.current_session()
            return ctx.id if ctx else None

    with mirascope.ops.session(id="base"):
        result = await task_with_override()
        assert result == "override"

        ctx = mirascope.ops.current_session()
        assert ctx is not None
        assert ctx.id == "base"


def test_extract_session_id_from_headers() -> None:
    """Extract session ID from carrier headers."""
    headers = {"Mirascope-Session-Id": "session-789"}

    session_id = extract_session_id(headers)

    assert session_id == "session-789"


@pytest.mark.parametrize(
    "headers",
    [
        {"mirascope-session-id": "lowercase"},
        {"MIRASCOPE-SESSION-ID": "uppercase"},
    ],
    ids=["lowercase", "uppercase"],
)
def test_extract_session_id_case_insensitive(headers: dict[str, str]) -> None:
    """Extract session ID with case-insensitive header name matching."""
    session_id = extract_session_id(headers)
    expected = headers[list(headers.keys())[0]]
    assert session_id == expected


@pytest.mark.parametrize(
    ("headers", "expected"),
    [
        ({"mirascope-Session-Id": ["session-abc", "session-def"]}, "session-abc"),
        ({"Other-Header": "value"}, None),
        ({"mirascope-Session-Id": []}, None),
        ({"Mirascope-Session-Id": ""}, None),
    ],
    ids=["list_first_value", "missing_header", "empty_list", "empty_string"],
)
def test_extract_session_id_edge_cases(
    headers: dict[str, str | list[str]], expected: str | None
) -> None:
    """Extract session ID from various edge case header formats."""
    session_id = extract_session_id(headers)
    assert session_id == expected


def test_session_with_attributes() -> None:
    """Create session with attributes."""
    attrs: dict[str, Jsonable] = {"environment": "production", "version": "1.0.0"}

    with mirascope.ops.session(id="attr-session", attributes=attrs):
        ctx = mirascope.ops.current_session()
        assert ctx is not None
        assert ctx.id == "attr-session"
        assert ctx.attributes == attrs


def test_current_session_without_context() -> None:
    """Return None when no session is active."""
    assert mirascope.ops.current_session() is None


def test_session_isolation_between_operations() -> None:
    """Ensure session context is isolated between operations."""
    with mirascope.ops.session(id="isolated-1"):
        ctx = mirascope.ops.current_session()
        assert ctx is not None
        assert ctx.id == "isolated-1"

    with mirascope.ops.session(id="isolated-2"):
        ctx = mirascope.ops.current_session()
        assert ctx is not None
        assert ctx.id == "isolated-2"
