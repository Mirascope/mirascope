from __future__ import annotations

from collections.abc import Generator

import pytest
from opentelemetry import trace as otel_trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter


@pytest.fixture
def span_exporter() -> Generator[InMemorySpanExporter, None, None]:
    """Fixture for providing an in-memory span exporter."""

    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    original = otel_trace._TRACER_PROVIDER
    otel_trace._TRACER_PROVIDER = provider
    try:
        yield exporter
    finally:
        provider.shutdown()
        exporter.clear()
        otel_trace._TRACER_PROVIDER = original
