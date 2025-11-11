"""Public OpenTelemetry helpers for `mirascope.llm`."""

from __future__ import annotations

from contextlib import suppress

from ._span import span

with suppress(ImportError):
    from .instrument_opentelemetry import (
        instrument_opentelemetry,
        is_instrumented,
        uninstrument_opentelemetry,
    )

__all__ = [
    "instrument_opentelemetry",
    "is_instrumented",
    "span",
    "uninstrument_opentelemetry",
]
