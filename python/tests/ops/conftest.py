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

from mirascope.ops._internal import configuration
from mirascope.ops._internal.instrumentation import llm
from mirascope.ops._internal.propagation import (
    ENV_PROPAGATOR_FORMAT,
    ENV_PROPAGATOR_SET_GLOBAL,
    PropagatorFormat,
    reset_propagator,
)

PROPAGATOR_FORMATS = list(get_args(PropagatorFormat))

_session_tracer_provider: TracerProvider | None = None


@pytest.fixture(scope="session", autouse=True)
def session_tracer_provider() -> Generator[TracerProvider, None, None]:
    """Set up a single TracerProvider for the test session."""
    global _session_tracer_provider
    provider = TracerProvider()
    otel_trace.set_tracer_provider(provider)
    _session_tracer_provider = provider
    yield provider
    provider.shutdown()


@pytest.fixture
def tracer_provider(session_tracer_provider: TracerProvider) -> TracerProvider:
    """Provide the session-scoped TracerProvider for tests that need it."""
    return session_tracer_provider


@pytest.fixture
def tracer(tracer_provider: TracerProvider) -> otel_trace.Tracer:
    """Get a tracer from the session TracerProvider."""
    return tracer_provider.get_tracer(__name__)


@pytest.fixture(autouse=True)
def reset_propagator_singleton() -> Generator[None, None, None]:
    """Reset propagator singleton and clean env vars before each test."""
    reset_propagator()
    yield
    reset_propagator()
    os.environ.pop(ENV_PROPAGATOR_FORMAT, None)
    os.environ.pop(ENV_PROPAGATOR_SET_GLOBAL, None)


def reset_configuration() -> None:
    """Reset configuration module state to defaults."""
    configuration._tracer_provider = None  # pyright: ignore[reportPrivateUsage]
    configuration._tracer_name = configuration.DEFAULT_TRACER_NAME  # pyright: ignore[reportPrivateUsage]
    configuration._tracer_version = None  # pyright: ignore[reportPrivateUsage]
    configuration._tracer = None  # pyright: ignore[reportPrivateUsage]


def reset_llm_instrumentation() -> None:
    """Reset llm instrumentation module state."""
    configuration.set_tracer(None)
    llm.llm._unwrap_model_call()  # pyright: ignore[reportPrivateUsage]


@pytest.fixture(autouse=True)
def reset_ops_configuration() -> Generator[None, None, None]:
    """Ensure ops.configure state does not leak across tests."""
    reset_configuration()
    yield
    reset_configuration()


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
def span_exporter(
    session_tracer_provider: TracerProvider,
) -> Generator[InMemorySpanExporter, None, None]:
    """Provide an in-memory span exporter for tracing assertions."""
    exporter = InMemorySpanExporter()
    processor = SimpleSpanProcessor(exporter)
    session_tracer_provider.add_span_processor(processor)
    try:
        yield exporter
    finally:
        exporter.clear()


@pytest.fixture
def valid_carrier() -> dict[str, str]:
    """Return a carrier dict pre-populated with a valid traceparent header."""
    return {"traceparent": VALID_TRACEPARENT}


@pytest.fixture(scope="session")
def vcr_config() -> dict[str, object]:
    """Return VCR.py configuration for ops tests."""
    return {
        "record_mode": "once",
        "match_on": ["method", "uri", "body"],
        "filter_headers": [
            "authorization",
            "cookie",
            "x-api-key",
            "x-goog-api-key",
        ],
        "filter_post_data_parameters": [],
    }
