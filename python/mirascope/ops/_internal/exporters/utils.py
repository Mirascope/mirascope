"""Utility functions for OpenTelemetry exporters.

This module provides helper functions for formatting and converting
OpenTelemetry data types for export.
"""


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
