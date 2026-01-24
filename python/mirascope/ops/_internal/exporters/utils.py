"""Utility functions for OpenTelemetry exporters.

This module provides helper functions for formatting and converting
OpenTelemetry data types for export.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from opentelemetry.util.types import AttributeValue


def to_otlp_any_value(value: AttributeValue) -> dict[str, object]:
    """Convert AttributeValue to OTLP AnyValue (dict form).

    - string/bool/int/float are converted to stringValue/boolValue/intValue/doubleValue
    - Sequence (excluding str/bytes/Mapping) is converted to arrayValue.values
    - Unsupported types fallback to stringValue=str(value)

    Args:
        value: An OpenTelemetry AttributeValue (bool, int, float, str, or Sequence)

    Returns:
        A dict representing OTLP AnyValue (e.g., {"stringValue": "..."})
    """
    match value:
        case str():
            return {"stringValue": value}
        case bool():
            return {"boolValue": value}
        case int():
            return {"intValue": str(value)}
        case float():
            return {"doubleValue": value}
        case _ if isinstance(value, bytes | bytearray | memoryview | Mapping):
            return {"stringValue": str(value)}
        case _ if isinstance(value, Sequence):
            values = [to_otlp_any_value(v) for v in value]
            return {"arrayValue": {"values": values}}
        case _:
            return {"stringValue": str(value)}


def format_trace_id(trace_id: int) -> str:
    """Format a trace ID as a 32-character hex string.

    Args:
        trace_id: The trace ID as an integer.

    Returns:
        32-character hexadecimal string representation of the trace ID.
    """
    return format(trace_id, "032x")


def format_span_id(span_id: int) -> str:
    """Format a span ID as a 16-character hex string.

    Args:
        span_id: The span ID as an integer.

    Returns:
        16-character hexadecimal string representation of the span ID.
    """
    return format(span_id, "016x")
