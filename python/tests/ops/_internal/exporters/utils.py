"""Shared test helpers for exporter tests."""

import time
from typing import Any
from unittest.mock import Mock

from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.trace import SpanContext, SpanKind, Status, StatusCode, TraceFlags
from opentelemetry.trace.span import TraceState


def create_mock_span(
    name: str = "test-span",
    span_id: int = 0x1234567890ABCDEF,
    trace_id: int = 0x123456789ABCDEF0123456789ABCDEF0,
    parent_span_id: int | None = None,
    shared_resource: Mock | None = None,
    kind: SpanKind = SpanKind.INTERNAL,
    status_code: StatusCode = StatusCode.OK,
    attributes: dict[str, Any] | None = None,
) -> Mock:
    """Create a mock ReadableSpan with common setup.

    Args:
        name: The span name
        span_id: The span ID (64-bit hex)
        trace_id: The trace ID (128-bit hex)
        parent_span_id: Optional parent span ID for nested spans
        shared_resource: Optional shared resource mock
        kind: The span kind (INTERNAL, SERVER, CLIENT, etc.)
        status_code: The span status code
        attributes: Optional span attributes

    Returns:
        A configured mock ReadableSpan
    """
    span = Mock(spec=ReadableSpan)
    span.name = name

    context = Mock(spec=SpanContext)
    context.trace_id = trace_id
    context.span_id = span_id
    context.trace_flags = TraceFlags(0x01)
    context.trace_state = TraceState()
    context.is_remote = False
    context.is_valid = True

    span.context = context
    span.get_span_context = Mock(return_value=context)

    if parent_span_id:
        span.parent = Mock(
            trace_id=trace_id,
            span_id=parent_span_id,
            trace_flags=TraceFlags(0x01),
            trace_state=TraceState(),
            is_remote=False,
            is_valid=True,
        )
    else:
        span.parent = None

    span.start_time = 1000000000000000000
    span.end_time = 1000000001000000000
    span.attributes = attributes or {}

    status_mock = Mock(spec=Status)
    status_mock.status_code = status_code
    status_mock.description = None
    span.status = status_mock

    span.events = []
    span.links = []
    span.kind = kind

    if shared_resource:
        span.resource = shared_resource
    else:
        span.resource = Mock()
        span.resource.attributes = {"service.name": "test-service"}

    span.instrumentation_scope = Mock()
    span.instrumentation_scope.name = "test-instrumentation"
    span.instrumentation_scope.version = "1.0.0"

    return span


def create_mock_span_with_time(
    name: str = "test_span",
    trace_id: int = 0x0102030405060708090A0B0C0D0E0F10,
    span_id: int = 0x0102030405060708,
) -> Mock:
    """Create a mock span with current time for retry/transport tests.

    This variant uses current time for start/end times and different
    default IDs for compatibility with existing retry tests.
    """
    span = Mock(spec=ReadableSpan)
    span.name = name

    context = Mock(spec=SpanContext)
    context.trace_id = trace_id
    context.span_id = span_id
    context.is_remote = False
    context.trace_flags = TraceFlags(0x01)
    context.trace_state = None

    span.context = context
    span.get_span_context = Mock(return_value=context)

    span.parent = None
    span.kind = SpanKind.SERVER
    span.start_time = int(time.time() * 1e9)
    span.end_time = int(time.time() * 1e9) + 1000000

    status_mock = Mock(spec=Status)
    status_mock.status_code = StatusCode.OK
    status_mock.description = None
    span.status = status_mock

    span.attributes = {}
    span.events = []
    span.links = []

    span.resource = Mock()
    span.resource.attributes = {"service.name": "test-service"}

    span.instrumentation_scope = Mock()
    span.instrumentation_scope.name = "test-scope"
    span.instrumentation_scope.version = "1.0.0"

    return span
