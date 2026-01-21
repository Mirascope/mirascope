"""Tests for context management utilities."""

from __future__ import annotations

import pytest
from opentelemetry import trace
from opentelemetry.context import Context
from opentelemetry.sdk.trace import TracerProvider

from mirascope import ops
from mirascope.ops import get_propagator, propagated_context, reset_propagator
from mirascope.ops._internal import propagation


def test_propagated_context_with_extract_from() -> None:
    """Successfully attach context extracted from carrier headers."""

    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("original-span") as original_span:
        carrier: dict[str, str] = {}
        propagation.inject_context(carrier)

        original_trace_id = original_span.get_span_context().trace_id

    with propagated_context(extract_from=carrier):
        current_span = trace.get_current_span()
        extracted_trace_id = current_span.get_span_context().trace_id

        assert extracted_trace_id == original_trace_id


def test_propagated_context_with_parent() -> None:
    """Successfully attach pre-existing parent context."""
    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("original-span") as original_span:
        parent_context = Context()
        parent_context = trace.set_span_in_context(original_span, parent_context)

        original_trace_id = original_span.get_span_context().trace_id

    with propagated_context(parent=parent_context):
        current_span = trace.get_current_span()
        attached_trace_id = current_span.get_span_context().trace_id

        assert attached_trace_id == original_trace_id


def test_propagated_context_raises_when_both_parameters() -> None:
    """Raise ValueError when both parent and extract_from are provided."""
    parent_context = Context()
    carrier = {"traceparent": "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01"}

    with (
        pytest.raises(ValueError) as exception_info,
        propagated_context(parent=parent_context, extract_from=carrier),
    ):
        pass

    assert "Cannot specify both" in str(exception_info.value)


def test_propagated_context_raises_when_no_parameters() -> None:
    """Raise ValueError when neither parent nor extract_from are provided."""
    with pytest.raises(ValueError) as exception_info, propagated_context():
        pass

    assert "Must specify either" in str(exception_info.value)


def test_propagated_context_detaches_on_exit() -> None:
    """Properly detach context after block exits."""

    provider = TracerProvider()
    tracer = provider.get_tracer(__name__)

    carrier: dict[str, str] = {}

    with tracer.start_as_current_span("separate-span") as separate_span:
        separate_context = trace.set_span_in_context(separate_span)
        propagation.inject_context(carrier, context=separate_context)

    with tracer.start_as_current_span("outer-span") as outer_span:
        outer_trace_id = outer_span.get_span_context().trace_id

        with propagated_context(extract_from=carrier):
            current_span_inside = trace.get_current_span()
            inside_trace_id = current_span_inside.get_span_context().trace_id
            assert inside_trace_id != outer_trace_id

        current_span_outside = trace.get_current_span()
        outside_trace_id = current_span_outside.get_span_context().trace_id
        assert outside_trace_id == outer_trace_id


def test_propagated_context_detaches_on_exception() -> None:
    """Properly detach context even when exception is raised inside block."""

    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("outer-span") as outer_span:
        outer_trace_id = outer_span.get_span_context().trace_id

        carrier: dict[str, str] = {}
        with tracer.start_as_current_span("inner-span"):
            propagation.inject_context(carrier)

        try:
            with propagated_context(extract_from=carrier):
                raise RuntimeError("test exception")
        except RuntimeError:
            pass

        current_span_after = trace.get_current_span()
        after_trace_id = current_span_after.get_span_context().trace_id
        assert after_trace_id == outer_trace_id


def test_propagated_context_with_invalid_carrier() -> None:
    """Attach empty context when carrier has invalid headers."""
    carrier = {"traceparent": "invalid-format"}

    with propagated_context(extract_from=carrier):
        current_span = trace.get_current_span()

        assert current_span is not None


def test_propagated_context_nested_calls() -> None:
    """Handle nested propagated_context calls correctly."""

    provider = TracerProvider()
    tracer = provider.get_tracer(__name__)

    carrier_outer: dict[str, str] = {}
    carrier_inner: dict[str, str] = {}

    with tracer.start_as_current_span("outer-span") as outer_span:
        outer_context = trace.set_span_in_context(outer_span)
        propagation.inject_context(carrier_outer, context=outer_context)

    with tracer.start_as_current_span("inner-span") as inner_span:
        inner_context = trace.set_span_in_context(inner_span)
        propagation.inject_context(carrier_inner, context=inner_context)

    with propagated_context(extract_from=carrier_outer):
        outer_context_span = trace.get_current_span()
        outer_trace_id = outer_context_span.get_span_context().trace_id

        with propagated_context(extract_from=carrier_inner):
            inner_context_span = trace.get_current_span()
            inner_trace_id = inner_context_span.get_span_context().trace_id

            assert inner_trace_id != outer_trace_id

        restored_span = trace.get_current_span()
        restored_trace_id = restored_span.get_span_context().trace_id

        assert restored_trace_id == outer_trace_id


def test_propagated_context_integration_with_span_creation() -> None:
    """Create spans inside context that have correct parent trace_id and span_id."""

    provider = TracerProvider()
    tracer = provider.get_tracer(__name__)

    parent_trace_id = None
    parent_span_id = None

    with tracer.start_as_current_span("parent-span") as parent_span:
        carrier: dict[str, str] = {}
        parent_context = trace.set_span_in_context(parent_span)
        propagation.inject_context(carrier, context=parent_context)

        parent_span_context = parent_span.get_span_context()
        parent_trace_id = parent_span_context.trace_id
        parent_span_id = parent_span_context.span_id

    with (
        propagated_context(extract_from=carrier),
        tracer.start_as_current_span("child-span") as child_span,
    ):
        child_span_context = child_span.get_span_context()
        child_trace_id = child_span_context.trace_id
        child_span_id = child_span_context.span_id

        assert child_trace_id == parent_trace_id
        assert child_span_id != parent_span_id


def test_propagated_context_with_empty_carrier() -> None:
    """Handle empty carrier dictionary without errors."""
    carrier: dict[str, str] = {}

    with propagated_context(extract_from=carrier):
        current_span = trace.get_current_span()

        assert current_span is not None


@pytest.mark.parametrize(
    ("carrier", "expected_session_id"),
    [
        (
            {
                "traceparent": "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01",
                "Mirascope-Session-Id": "extracted-session-123",
            },
            "extracted-session-123",
        ),
        (
            {
                "traceparent": "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01",
                "Mirascope-session-id": "lowercase-session",
            },
            "lowercase-session",
        ),
        (
            {"traceparent": "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01"},
            None,
        ),
    ],
    ids=["standard_header", "case_insensitive", "no_session_header"],
)
def test_propagated_context_session_extraction(
    carrier: dict[str, str], expected_session_id: str | None
) -> None:
    """Extract session from carrier headers with various formats."""
    with propagated_context(extract_from=carrier):
        ctx = ops.current_session()
        if expected_session_id is None:
            assert ctx is None
        else:
            assert ctx is not None
            assert ctx.id == expected_session_id


def test_propagated_context_session_override() -> None:
    """Allow explicit session override within propagated context."""
    carrier: dict[str, str] = {
        "traceparent": "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01",
        "Mirascope-Session-Id": "propagated-session",
    }

    with propagated_context(extract_from=carrier):
        ctx = ops.current_session()
        assert ctx is not None
        assert ctx.id == "propagated-session"

        with ops.session(id="override-session"):
            ctx = ops.current_session()
            assert ctx is not None
            assert ctx.id == "override-session"

        ctx = ops.current_session()
        assert ctx is not None
        assert ctx.id == "propagated-session"


def test_propagated_context_session_cleanup_on_exception() -> None:
    """Restore session state after exception in propagated context."""
    carrier: dict[str, str] = {
        "traceparent": "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01",
        "Mirascope-Session-Id": "exception-session",
    }

    assert ops.current_session() is None

    try:
        with propagated_context(extract_from=carrier):
            assert ops.current_session() is not None
            raise RuntimeError("test exception")
    except RuntimeError:
        pass

    assert ops.current_session() is None


@pytest.mark.parametrize(
    ("propagator_format", "expected_header"),
    [
        ("tracecontext", "traceparent"),
        ("b3", "b3"),
        ("b3multi", "x-b3-traceid"),
        ("jaeger", "uber-trace-id"),
        ("composite", "traceparent"),
    ],
    ids=["tracecontext", "b3", "b3multi", "jaeger", "composite"],
)
def test_propagated_context_with_various_propagators(
    monkeypatch: pytest.MonkeyPatch,
    propagator_format: str,
    expected_header: str,
) -> None:
    """Verify all propagators work with session extraction."""
    monkeypatch.setenv("MIRASCOPE_PROPAGATOR", propagator_format)
    reset_propagator()

    provider = TracerProvider()
    tracer = provider.get_tracer(__name__)
    propagator = get_propagator()

    with tracer.start_as_current_span(f"{propagator_format}-span") as original_span:
        carrier: dict[str, str] = {}
        carrier["Mirascope-Session-Id"] = f"{propagator_format}-session-123"
        propagator.inject_context(carrier)

        original_trace_id = original_span.get_span_context().trace_id

    assert expected_header in carrier

    with propagated_context(extract_from=carrier):
        current_span = trace.get_current_span()
        extracted_trace_id = current_span.get_span_context().trace_id
        assert extracted_trace_id == original_trace_id

        ctx = ops.current_session()
        assert ctx is not None
        assert ctx.id == f"{propagator_format}-session-123"
