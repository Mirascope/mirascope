from __future__ import annotations

import os
import re
from collections.abc import Generator
from typing import get_args

import pytest
from opentelemetry import trace as otel_trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from mirascope.ops import PropagatorFormat, reset_propagator
from mirascope.ops._internal.propagation import (
    ENV_PROPAGATOR_FORMAT,
    ENV_PROPAGATOR_SET_GLOBAL,
)

PROPAGATOR_FORMATS = list(get_args(PropagatorFormat))


@pytest.fixture(autouse=True)
def reset_propagator_singleton() -> Generator[None, None, None]:
    """Reset propagator singleton and clean up env vars before each test."""
    reset_propagator()
    yield
    reset_propagator()
    os.environ.pop(ENV_PROPAGATOR_FORMAT, None)
    os.environ.pop(ENV_PROPAGATOR_SET_GLOBAL, None)


VALID_TRACEPARENT = "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01"
VALID_TRACE_ID = int("0af7651916cd43dd8448eb211c80319c", 16)
VALID_SPAN_ID = int("b7ad6b7169203331", 16)

TRACEPARENT_PATTERN = re.compile(r"^00-[0-9a-f]{32}-[0-9a-f]{16}-01$")

TRACEPARENT_REGEX = re.compile(
    r"^(?P<version>[0-9a-f]{2})-"
    r"(?P<trace_id>[0-9a-f]{32})-"
    r"(?P<span_id>[0-9a-f]{16})-"
    r"(?P<trace_flags>[0-9a-f]{2})$"
)


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


@pytest.fixture
def valid_carrier() -> dict[str, str]:
    """Fixture providing a valid carrier with traceparent header."""
    return {"traceparent": VALID_TRACEPARENT}
