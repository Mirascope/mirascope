"""Type definitions for the two-phase export system.

This module defines the event types and data structures used for
immediate start event transmission and batched end event export.
"""

from enum import Enum
from typing import Literal, TypedDict

from opentelemetry.util.types import AttributeValue

# TODO: unify/DRY types in the _internal package

SpanKind = Literal["CLIENT", "SERVER", "PRODUCER", "CONSUMER", "INTERNAL"]
StatusCode = Literal["UNSET", "OK", "ERROR"]


class SpanEventType(str, Enum):
    """Event types for span lifecycle tracking."""

    SPAN_STARTED = "span_started"
    SPAN_UPDATED = "span_updated"
    SPAN_COMPLETED = "span_completed"


class SpanEvent(TypedDict):
    """Individual event within a span."""

    name: str
    """The name of the event."""

    timestamp: int
    """Nanoseconds since epoch (OTel standard)."""

    attributes: dict[str, AttributeValue]
    """Event-specific attributes."""


class Status(TypedDict):
    """Status representation for serialization."""

    code: StatusCode
    """The status code: UNSET, OK, or ERROR."""

    description: str | None
    """Optional human-readable description of the status."""


class SpanContextDict(TypedDict):
    """Span context for links and parent references."""

    trace_id: str
    """The trace ID as a 32-character hex string."""

    span_id: str
    """The span ID as a 16-character hex string."""

    trace_flags: int
    """Trace flags (e.g., for sampling decisions)."""

    trace_state: str | None
    """Optional vendor-specific trace state."""


class Link(TypedDict):
    """Link representation for span relationships."""

    context: SpanContextDict
    """The linked span's context."""

    attributes: dict[str, AttributeValue]
    """Attributes describing the link."""


class SpanStartEvent(TypedDict):
    """Minimal span data for immediate transmission.

    This event is sent immediately when a span starts to provide
    real-time visibility into long-running operations.
    """

    trace_id: str
    """The trace ID as a 32-character hex string."""

    span_id: str
    """The span ID as a 16-character hex string."""

    parent_span_id: str | None
    """The parent span ID if this is a child span."""

    name: str
    """The name of the span."""

    start_time: int
    """Nanoseconds since epoch."""

    kind: SpanKind
    """The span kind: CLIENT, SERVER, PRODUCER, CONSUMER, or INTERNAL."""

    attributes: dict[str, AttributeValue]
    """Minimal required attributes only."""


class SpanUpdateEvent(TypedDict, total=False):
    """Incremental updates to span data.

    These events are batched and sent periodically to update
    span attributes or add events without waiting for completion.
    """

    trace_id: str
    """The trace ID as a 32-character hex string."""

    span_id: str
    """The span ID as a 16-character hex string."""

    timestamp: int
    """Nanoseconds since epoch."""

    attributes: dict[str, AttributeValue]
    """Additional or updated attributes."""

    events: list[SpanEvent]
    """New events to add to the span."""


class SpanCompleteEvent(TypedDict):
    """Complete span data for batch export.

    This event contains all span data and is sent when the span
    completes, typically in batches for efficiency.
    """

    trace_id: str
    """The trace ID as a 32-character hex string."""

    span_id: str
    """The span ID as a 16-character hex string."""

    parent_span_id: str | None
    """The parent span ID if this is a child span."""

    name: str
    """The name of the span."""

    kind: SpanKind
    """The span kind: CLIENT, SERVER, PRODUCER, CONSUMER, or INTERNAL."""

    start_time: int
    """Nanoseconds since epoch."""

    end_time: int
    """Nanoseconds since epoch."""

    status: Status
    """The final status of the span."""

    attributes: dict[str, AttributeValue]
    """All span attributes."""

    events: list[SpanEvent]
    """All events that occurred during the span."""

    links: list[Link]
    """Links to other spans."""
