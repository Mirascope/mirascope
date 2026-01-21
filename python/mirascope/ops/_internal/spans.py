"""Explicit span management utilities for `mirascope.ops`."""

from __future__ import annotations

import logging
from contextvars import Token
from typing import TYPE_CHECKING, Any

from opentelemetry import context as otel_context, trace as otel_trace
from opentelemetry.trace import (
    SpanContext,
    Status,
    StatusCode,
    format_span_id,
    format_trace_id,
)
from opentelemetry.util.types import AttributeValue

from .session import current_session
from .utils import json_dumps

if TYPE_CHECKING:
    from opentelemetry.context import Context

logger = logging.getLogger("mirascope.ops")
_warned_noop = False


class Span:
    """Context-managed span for explicit tracing.

    Creates a child span within the current trace context. Acts as a no-op
    if tracing is not configured.
    """

    def __init__(self, name: str, **attributes: AttributeValue) -> None:
        """Initialize a new span with the given name.

        Args:
            name: Name for the span.
            **attributes: Initial attributes to set on the span.
        """
        self._name = name
        self._initial_attributes = attributes
        self._span: otel_trace.Span | None = None
        self._token: Token[Context] | None = None
        self._is_noop = True
        self._finished = False

    def __enter__(self) -> Span:
        """Enter the span context.

        Returns:
            This span instance for use within the context.
        """
        tracer = otel_trace.get_tracer("mirascope.ops")
        self._span = tracer.start_span(self._name)

        if self._span.__class__.__name__ == "NonRecordingSpan":
            self._is_noop = True
            self._span = None
            global _warned_noop
            if not _warned_noop:
                logger.warning(
                    f"mirascope tracing is not configured; Span('{self._name}') is a no-op."
                )
                _warned_noop = True
        else:
            self._is_noop = False
            self._span.set_attribute("mirascope.type", "trace")

            session_ctx = current_session()
            if session_ctx is not None:
                self._span.set_attribute("mirascope.ops.session.id", session_ctx.id)
                if session_ctx.attributes is not None:
                    self._span.set_attribute(
                        "mirascope.ops.session.attributes",
                        json_dumps(session_ctx.attributes),
                    )

            self._token = otel_context.attach(
                otel_trace.set_span_in_context(self._span)
            )

            if self._initial_attributes:
                self.set(**self._initial_attributes)

        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: Any,  # noqa: ANN401
    ) -> None:
        """Exit the span context.

        Args:
            exc_type: Exception type if an exception was raised.
            exc: Exception instance if an exception was raised.
            tb: Traceback if an exception was raised.
        """
        if self._span and not self._finished:
            if exc is not None:
                self._span.record_exception(exc)
                self._span.set_status(Status(StatusCode.ERROR))
            self.finish()

    def set(self, **attributes: AttributeValue) -> None:
        """Set attributes on the current span.

        Args:
            **attributes: Key-value pairs to set as span attributes.
        """
        if self._span and not self._finished:
            for key, value in attributes.items():
                self._span.set_attribute(key, value)

    def event(self, name: str, **attributes: AttributeValue) -> None:
        """Record an event within the span.

        Args:
            name: Name of the event.
            **attributes: Event attributes as key-value pairs.
        """
        if self._span and not self._finished:
            self._span.add_event(name, attributes=attributes)

    def debug(self, message: str, **additional_attributes: AttributeValue) -> None:
        """Log a debug message within the span.

        Args:
            message: Debug message text.
            **additional_attributes: Additional structured attributes for the log entry.
        """
        self.event("debug", level="debug", message=message, **additional_attributes)

    def info(self, message: str, **additional_attributes: AttributeValue) -> None:
        """Log an info message within the span.

        Args:
            message: Info message text.
            **additional_attributes: Additional structured attributes for the log entry.
        """
        self.event("info", level="info", message=message, **additional_attributes)

    def warning(self, message: str, **additional_attributes: AttributeValue) -> None:
        """Log a warning message within the span.

        Args:
            message: Warning message text.
            **additional_attributes: Additional structured attributes for the log entry.
        """
        self.event("warning", level="warning", message=message, **additional_attributes)

    def error(self, message: str, **additional_attributes: AttributeValue) -> None:
        """Log an error message within the span.

        Args:
            message: Error message text.
            **additional_attributes: Additional structured attributes for the log entry.
        """
        self.event("error", level="error", message=message, **additional_attributes)
        if self._span and not self._finished:
            self._span.set_status(Status(StatusCode.ERROR))

    def critical(self, message: str, **additional_attributes: AttributeValue) -> None:
        """Log a critical message within the span.

        Args:
            message: Critical message text.
            **additional_attributes: Additional structured attributes for the log entry.
        """
        self.event("critical", level="error", message=message, **additional_attributes)
        if self._span and not self._finished:
            self._span.set_status(Status(StatusCode.ERROR))

    def finish(self) -> None:
        """Explicitly finish the span."""
        if not self._finished:
            self._finished = True
            if self._span:
                self._span.end()
            if self._token:
                otel_context.detach(self._token)
                self._token = None

    @property
    def span_id(self) -> str | None:
        """Get the span ID if available.

        Returns:
            The span ID or None if not available.
        """
        if span_context := self.span_context:
            return format_span_id(span_context.span_id)
        return None

    @property
    def trace_id(self) -> str | None:
        if span_context := self.span_context:
            return format_trace_id(span_context.trace_id)
        return None

    @property
    def is_noop(self) -> bool:
        """Check if this is a no-op span.

        Returns:
            True if tracing is disabled, False otherwise.
        """
        return self._is_noop

    @property
    def span_context(self) -> SpanContext | None:
        """Return the span context if available."""
        if otel_span := self._span:
            return otel_span.get_span_context()
        return None


def span(name: str, **attributes: AttributeValue) -> Span:
    """Create a new span context manager.

    Args:
        name: Name for the new span.
        **attributes: Initial attributes to set on the span.

    Returns:
        A Span context manager that creates a child span when entered.
    """
    return Span(name, **attributes)
