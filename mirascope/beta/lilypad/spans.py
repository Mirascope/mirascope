"""A context manager for creating a tracing span with parent-child relationship tracking,"""

import datetime
import json
import threading
from collections.abc import Generator
from contextlib import AbstractContextManager, contextmanager
from types import TracebackType
from typing import Any

from opentelemetry import context as context_api
from opentelemetry.trace import Span as OTSpan
from opentelemetry.trace import StatusCode, get_tracer, set_span_in_context

# Global counter and lock for span order.
_span_counter_lock = threading.Lock()
_span_counter = 0


@contextmanager
def span_order_context(span: OTSpan) -> Generator[None, None, None]:
    """Assign an explicit order to a span using a global counter."""
    global _span_counter
    with _span_counter_lock:
        _span_counter += 1
    yield


class Span:
    """A context manager for creating a tracing span with parent-child relationship tracking."""

    def __init__(self, name: str) -> None:
        self.name: str = name
        self._span: OTSpan | None = None
        self._span_cm: AbstractContextManager[OTSpan] | None = None
        self._order_cm: AbstractContextManager[Any] | None = None
        self._finished: bool = False
        self._token = None

    def __enter__(self) -> "Span":
        tracer = get_tracer("lilypad")
        self._span = tracer.start_span(self.name)
        self._span.set_attribute("lilypad.type", "trace")

        self._current_context = context_api.get_current()
        ctx = set_span_in_context(self._span, self._current_context)
        # Activate our context
        self._token = context_api.attach(ctx)

        self._order_cm = span_order_context(self._span)
        self._order_cm.__enter__()

        self.metadata(
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
        )
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None and self._span is not None and exc_val is not None:
            self._span.record_exception(exc_val)
        if self._order_cm is not None:
            self._order_cm.__exit__(exc_type, exc_val, exc_tb)

        if self._span is not None:
            self._span.end()

        if self._token:
            context_api.detach(self._token)

        self._finished = True

    async def __aenter__(self) -> "Span":
        return self.__enter__()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.__exit__(exc_type, exc_val, exc_tb)

    def _log_event(self, level: str, message: str, **kwargs: Any) -> None:  # noqa: ANN401
        if self._span is not None:
            attributes: dict[str, Any] = {
                f"{level}.message": message,
            }
            if level in ("error", "critical"):
                self._span.set_status(StatusCode.ERROR)
            attributes |= kwargs
            self._span.add_event(level, attributes=attributes)

    def debug(self, message: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Log a debug message."""
        self._log_event("debug", message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Log an informational message."""
        self._log_event("info", message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Alias for the warning method."""
        self._log_event("warning", message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Alias for the error method."""
        self._log_event("error", message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Alias for the critical method."""
        self._log_event("critical", message, **kwargs)

    def log(self, message: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Alias for the info method."""
        self.info(message, **kwargs)

    def metadata(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        """Enhance structured logging by setting metadata attributes.

        Accepts either a dictionary as the first argument or key-value pairs.
        Non-primitive values are automatically serialized to JSON.
        """
        if self._span is None:
            return
        if args and isinstance(args[0], dict):
            data: dict[str, Any] = args[0].copy()
            data |= kwargs
        else:
            data = kwargs

        for key, value in data.items():
            if not isinstance(value, str | int | float | bool) and value is not None:
                try:
                    value = json.dumps(value)
                except Exception:
                    value = str(value)
            self._span.set_attribute(key, value)

    def finish(self) -> None:
        """Explicitly finish the span if it has not been ended yet."""
        if not self._finished and self._span is not None:
            self._span.end()

            if self._token:
                context_api.detach(self._token)
            self._finished = True


def span(name: str) -> Span:
    """Convenience function to create a Span context manager."""
    return Span(name)
