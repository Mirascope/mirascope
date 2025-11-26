"""Tests for Span explicit tracing functionality."""

from __future__ import annotations

import logging
from collections.abc import Generator

import pytest
from inline_snapshot import snapshot
from opentelemetry import trace as otel_trace
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import (
    NonRecordingSpan,
    SpanContext,
    TraceFlags,
    TraceState,
    format_span_id,
    format_trace_id,
)

import mirascope

from .utils import extract_span_data


class _StaticNoOpTracer:
    """A static no-op tracer that always returns non-recording spans."""

    def start_span(self, name: str) -> NonRecordingSpan:
        """Create a new non-recording span."""
        context = SpanContext(
            trace_id=0x1234567890ABCDEF1234567890ABCDEF,
            span_id=0x1234567890ABCDEF,
            is_remote=False,
            trace_flags=TraceFlags(0x01),
            trace_state=TraceState(),
        )
        return NonRecordingSpan(context)


class _StaticNoOpProvider:
    """A static no-op tracer provider for testing noop span behavior."""

    def get_tracer(
        self,
        name: str,
        version: str | None = None,
        schema_url: str | None = None,
        attributes: dict[str, object] | None = None,
    ) -> _StaticNoOpTracer:
        return _StaticNoOpTracer()


@pytest.fixture
def noop_provider() -> Generator[None, None, None]:
    """Fixture that provides a no-op tracer provider for testing."""
    original_provider = otel_trace._TRACER_PROVIDER  # pyright: ignore[reportPrivateUsage]
    otel_trace._TRACER_PROVIDER = _StaticNoOpProvider()  # pyright: ignore[reportPrivateUsage]
    try:
        yield
    finally:
        otel_trace._TRACER_PROVIDER = original_provider  # pyright: ignore[reportPrivateUsage]


def test_noop_span_basic(noop_provider: None) -> None:
    """Test that no-op span handles all operations safely without errors."""
    with mirascope.ops.span("noop") as span:
        assert span.is_noop is True
        assert span.span_id is None

        span.set(a=1, b="x")
        span.event("check", ok=True)
        span.debug("dbg")
        span.info("inf")
        span.warning("warn")
        span.error("err")
        span.critical("crit")


def test_noop_span_with_exception(noop_provider: None) -> None:
    """Test that no-op span handles exceptions gracefully without recording."""
    with (
        pytest.raises(ValueError, match="test error"),
        mirascope.ops.span("error-phase") as span,
    ):
        span.set(test=True)
        raise ValueError("test error")


def test_span_records_attributes_and_events(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that configured span records attributes and events correctly."""
    with mirascope.ops.span("op") as span:
        assert span.is_noop is False
        assert span.span_id is not None

        span.set(a=1, b="x")
        span.event("evt", ok=True)
        span.error("boom", code=500)

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span = spans[0]
    assert extract_span_data(span) == snapshot(
        {
            "name": "op",
            "attributes": {"mirascope.type": "trace", "a": 1, "b": "x"},
            "status": {"status_code": "ERROR", "description": None},
            "events": [
                {"name": "evt", "attributes": {"ok": True}},
                {
                    "name": "error",
                    "attributes": {"message": "boom", "level": "error", "code": 500},
                },
            ],
        }
    )


def test_span_full_lifecycle(span_exporter: InMemorySpanExporter) -> None:
    """Test complete span lifecycle with all logging methods and attributes."""
    with mirascope.ops.span("lifecycle") as span:
        span.set(phase="start", version="1.0", env="test")
        span.debug("Starting process", step=1)
        span.info("Process initialized", ready=True)
        span.warning("Low memory", available_mb=256)
        span.event("custom", data='{"key":"value"}')
        span.error("Connection failed", host="localhost")
        span.critical("System failure", code="CRITICAL_001")

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span = spans[0]
    assert extract_span_data(span) == snapshot(
        {
            "name": "lifecycle",
            "attributes": {
                "mirascope.type": "trace",
                "phase": "start",
                "version": "1.0",
                "env": "test",
            },
            "status": {"status_code": "ERROR", "description": None},
            "events": [
                {
                    "name": "debug",
                    "attributes": {
                        "message": "Starting process",
                        "level": "debug",
                        "step": 1,
                    },
                },
                {
                    "name": "info",
                    "attributes": {
                        "message": "Process initialized",
                        "level": "info",
                        "ready": True,
                    },
                },
                {
                    "name": "warning",
                    "attributes": {
                        "message": "Low memory",
                        "level": "warning",
                        "available_mb": 256,
                    },
                },
                {"name": "custom", "attributes": {"data": '{"key":"value"}'}},
                {
                    "name": "error",
                    "attributes": {
                        "message": "Connection failed",
                        "level": "error",
                        "host": "localhost",
                    },
                },
                {
                    "name": "critical",
                    "attributes": {
                        "message": "System failure",
                        "level": "error",
                        "code": "CRITICAL_001",
                    },
                },
            ],
        }
    )


def test_span_with_exception_recording(span_exporter: InMemorySpanExporter) -> None:
    """Test that span records exceptions properly with ERROR status."""
    with (
        pytest.raises(RuntimeError, match="Something went wrong"),
        mirascope.ops.span("exception-test") as span,
    ):
        span.set(operation="risky")
        raise RuntimeError("Something went wrong")

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span = spans[0]
    span_data = extract_span_data(span)
    assert span_data["name"] == "exception-test"
    assert span_data["attributes"] == snapshot(
        {"mirascope.type": "trace", "operation": "risky"}
    )
    assert span_data["status"] == snapshot(
        {"status_code": "ERROR", "description": None}
    )

    events = span_data.get("events", [])
    assert isinstance(events, list)
    assert len([e for e in events if e["name"] == "exception"]) == 1


def test_span_nested_contexts(span_exporter: InMemorySpanExporter) -> None:
    """Test nested span contexts create proper parent-child relationships."""
    with mirascope.ops.span("parent") as parent:
        parent.set(level=1)
        with mirascope.ops.span("child") as child:
            child.set(level=2)
            with mirascope.ops.span("grandchild") as grandchild:
                grandchild.set(level=3)

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 3

    assert extract_span_data(spans[0]) == snapshot(
        {
            "name": "grandchild",
            "attributes": {"mirascope.type": "trace", "level": 3},
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )
    assert extract_span_data(spans[1]) == snapshot(
        {
            "name": "child",
            "attributes": {"mirascope.type": "trace", "level": 2},
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )
    assert extract_span_data(spans[2]) == snapshot(
        {
            "name": "parent",
            "attributes": {"mirascope.type": "trace", "level": 1},
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


def test_span_id_format(span_exporter: InMemorySpanExporter) -> None:
    """Test that span_id is properly formatted as 16-character hex string."""
    with mirascope.ops.span("format-test") as span:
        span_id = span.span_id
        assert span_id is not None
        assert len(span_id) == 16
        assert all(c in "0123456789abcdef" for c in span_id)


def test_span_concurrent_operations(span_exporter: InMemorySpanExporter) -> None:
    """Test that multiple spans can operate independently without interference."""
    with mirascope.ops.span("operation-1") as span1:
        span1.set(task="first")
        with mirascope.ops.span("operation-2") as span2:
            span2.set(task="second")
            span1.event("still-active")
            span2.event("concurrent")

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 2

    assert extract_span_data(spans[0]) == snapshot(
        {
            "name": "operation-2",
            "attributes": {"mirascope.type": "trace", "task": "second"},
            "status": {"status_code": "UNSET", "description": None},
            "events": [{"name": "concurrent", "attributes": {}}],
        }
    )
    assert extract_span_data(spans[1]) == snapshot(
        {
            "name": "operation-1",
            "attributes": {"mirascope.type": "trace", "task": "first"},
            "status": {"status_code": "UNSET", "description": None},
            "events": [{"name": "still-active", "attributes": {}}],
        }
    )


def test_noop_span_logs_once(
    caplog: pytest.LogCaptureFixture, noop_provider: _StaticNoOpProvider
) -> None:
    """Test that warning logs exactly once when spans operate in no-op mode."""
    from mirascope.ops._internal import spans as span_module

    span_module._warned_noop = False  # pyright: ignore[reportPrivateUsage]
    with caplog.at_level(logging.WARNING, logger="mirascope"):
        with mirascope.ops.span("noop-log") as first:
            assert first.is_noop is True
            assert first.span_id is None
            assert first.trace_id is None
            assert first.span_context is None
        with mirascope.ops.span("noop-log-second") as second:
            assert second.is_noop is True
            assert second.span_id is None
            assert second.trace_id is None
            assert second.span_context is None

    warnings = [
        record
        for record in caplog.records
        if "mirascope tracing is not configured" in record.getMessage()
    ]
    assert len(warnings) == 1


def test_span_preserves_complex_attributes(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that complex attributes and events are preserved as sequences/strings."""
    with mirascope.ops.span("complex") as span:
        span.set(numbers=[1, 2, 3], payload='{"ok": true}')
        span.event("details", points=[1, 2], info='{"nested": "yes"}')

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    data = extract_span_data(spans[0])
    assert data == snapshot(
        {
            "name": "complex",
            "attributes": {
                "mirascope.type": "trace",
                "numbers": (1, 2, 3),
                "payload": '{"ok": true}',
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [
                {
                    "name": "details",
                    "attributes": {
                        "points": (1, 2),
                        "info": '{"nested": "yes"}',
                    },
                }
            ],
        }
    )


def test_span_trace_and_context_properties(span_exporter: InMemorySpanExporter) -> None:
    """Test that trace/span IDs are exposed and context round-trips correctly."""
    with mirascope.ops.span("context-check") as span:
        trace_id = span.trace_id
        span_id = span.span_id
        context = span.span_context

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    otel_context = spans[0].get_span_context()
    assert otel_context is not None
    assert trace_id == format_trace_id(otel_context.trace_id)
    assert span_id == format_span_id(otel_context.span_id)
    assert context == otel_context


def test_span_with_session(span_exporter: InMemorySpanExporter) -> None:
    """Test that span records session ID from active session."""
    with (
        mirascope.ops.session(id="session-123"),
        mirascope.ops.span("op-with-session") as span,
    ):
        span.set(task="test")

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data == snapshot(
        {
            "name": "op-with-session",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.ops.session.id": "session-123",
                "task": "test",
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


def test_span_with_session_attributes(span_exporter: InMemorySpanExporter) -> None:
    """Test that span records session ID and attributes."""
    with (
        mirascope.ops.session(
            id="session-456", attributes={"user": "alice", "env": "prod"}
        ),
        mirascope.ops.span("op-with-attrs"),
    ):
        pass

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data == snapshot(
        {
            "name": "op-with-attrs",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.ops.session.id": "session-456",
                "mirascope.ops.session.attributes": '{"user":"alice","env":"prod"}',
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


def test_span_without_session(span_exporter: InMemorySpanExporter) -> None:
    """Test that span works without active session."""
    with mirascope.ops.span("op-no-session") as span:
        span.set(task="test")

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data == snapshot(
        {
            "name": "op-no-session",
            "attributes": {"mirascope.type": "trace", "task": "test"},
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


def test_span_nested_session_override(span_exporter: InMemorySpanExporter) -> None:
    """Test that nested session correctly overrides parent session."""
    with mirascope.ops.session(id="outer-session"):
        with mirascope.ops.span("outer-span"):
            pass

        with (
            mirascope.ops.session(id="inner-session"),
            mirascope.ops.span("inner-span"),
        ):
            pass

        with mirascope.ops.span("outer-span-2"):
            pass

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 3

    assert extract_span_data(spans[0]) == snapshot(
        {
            "name": "outer-span",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.ops.session.id": "outer-session",
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )
    assert extract_span_data(spans[1]) == snapshot(
        {
            "name": "inner-span",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.ops.session.id": "inner-session",
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )
    assert extract_span_data(spans[2]) == snapshot(
        {
            "name": "outer-span-2",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.ops.session.id": "outer-session",
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


def test_span_with_initial_attributes(span_exporter: InMemorySpanExporter) -> None:
    """Test that span accepts initial attributes in constructor."""
    with mirascope.ops.span("init-attrs", user_id="123", action="process") as span:
        span.set(additional="value")

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data == snapshot(
        {
            "name": "init-attrs",
            "attributes": {
                "mirascope.type": "trace",
                "user_id": "123",
                "action": "process",
                "additional": "value",
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


def test_span_with_initial_complex_attributes(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that span accepts complex initial attributes without serialization."""
    with mirascope.ops.span("complex-init", tags=["a", "b"], config='{"key":"val"}'):
        pass

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data == snapshot(
        {
            "name": "complex-init",
            "attributes": {
                "mirascope.type": "trace",
                "tags": ("a", "b"),
                "config": '{"key":"val"}',
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


def test_noop_span_with_initial_attributes(noop_provider: None) -> None:
    """Test that no-op span handles initial attributes without errors."""
    with mirascope.ops.span("noop-init", user_id="456", count=3) as span:
        assert span.is_noop is True
        assert span.span_id is None
