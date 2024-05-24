"""Configuration for the Mirascope otel module tests."""
from dataclasses import dataclass
from typing import cast

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import (
    ProxyTracerProvider,
    Tracer,
    get_tracer,
    get_tracer_provider,
    set_tracer_provider,
)


@dataclass
class CapOtel:
    exporter: InMemorySpanExporter
    tracer: Tracer


@pytest.fixture(scope="module")
def fixture_capotel() -> CapOtel:
    exporter = InMemorySpanExporter()
    tracer_provider = get_tracer_provider()
    if isinstance(tracer_provider, ProxyTracerProvider):  # pragma: no cover
        tracer_provider = TracerProvider()  # Runs when otel tests are run in insolation
    cast(TracerProvider, tracer_provider).add_span_processor(
        SimpleSpanProcessor(exporter)
    )
    set_tracer_provider(tracer_provider)
    # NOTE: Setting trace_provider in get_tracer
    # bypasses global tracer provider set by logfire
    tracer = get_tracer(
        instrumenting_module_name="otel", tracer_provider=tracer_provider
    )
    return CapOtel(exporter, tracer)
