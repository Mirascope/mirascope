from __future__ import annotations

import json
import re
from collections.abc import Mapping
from contextlib import suppress
from typing import TypedDict

from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.util.types import AttributeValue

_OBJECT_ADDRESS_PATTERN = re.compile(r" at 0x[0-9a-fA-F]+")


class SpanStatus(TypedDict):
    """Span status information."""

    status_code: str
    description: str | None


class SpanEvent(TypedDict):
    """Span event information."""

    name: str
    attributes: dict[str, AttributeValue]


class SpanData(TypedDict):
    """Complete span data for testing."""

    name: str
    attributes: dict[str, AttributeValue]
    status: SpanStatus
    events: list[SpanEvent]


def extract_span_data(span: ReadableSpan) -> SpanData:
    """Extract serializable data from a span for snapshot testing.

    Automatically parses known JSON string attributes from OpenTelemetry GenAI
    semantic conventions for easier snapshot assertions.

    Args:
        span: The span to extract data from

    Returns:
        Dictionary containing span name, attributes, status, and events
    """
    attributes = dict(span.attributes) if span.attributes else {}

    json_attribute_keys = [
        "gen_ai.input.messages",
        "gen_ai.output.messages",
        "gen_ai.system_instructions",
    ]

    for key in json_attribute_keys:
        if (value := attributes.get(key)) and isinstance(value, str):
            with suppress(json.JSONDecodeError, TypeError):
                attributes[key] = json.loads(value)

    return {
        "name": span.name,
        "attributes": attributes,
        "status": {
            "status_code": span.status.status_code.name,
            "description": span.status.description,
        },
        "events": [
            {
                "name": event.name,
                "attributes": dict(event.attributes) if event.attributes else {},
            }
            for event in span.events
        ],
    }


class SpanSnapshot(TypedDict):
    name: str
    kind: str
    status: str
    attributes: Mapping[str, object]


def span_snapshot(span: ReadableSpan) -> SpanSnapshot:
    """Return snapshot-ready span metadata extracted from a ReadableSpan."""
    attrs = span.attributes or {}
    serializable_attrs: dict[str, object] = {
        key: list(value) if isinstance(value, tuple) else value
        for key, value in attrs.items()
    }
    return {
        "name": span.name,
        "kind": span.kind.name,
        "status": span.status.status_code.name,
        "attributes": serializable_attrs,
    }
