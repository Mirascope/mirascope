"""Test fixtures for exporters module."""

import os
import time
from unittest.mock import Mock

import pytest
from dotenv import load_dotenv
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import SpanContext, SpanKind, Status, StatusCode

from mirascope.api.client import Mirascope, get_sync_client
from mirascope.ops._internal.exporters.exporters import MirascopeOTLPExporter
from mirascope.ops._internal.exporters.processors import MirascopeSpanProcessor


@pytest.fixture
def mirascope_api_key() -> str:
    """Get Mirascope API key from environment or return dummy key."""
    load_dotenv()
    return os.getenv("MIRASCOPE_API_KEY", "test-api-key")


@pytest.fixture
def span() -> Mock:
    """Create a mock ReadableSpan for testing."""
    span = Mock(spec=ReadableSpan)
    span.name = "test_span"

    context = Mock(spec=SpanContext)
    context.trace_id = 0x0102030405060708090A0B0C0D0E0F10
    context.span_id = 0x0102030405060708
    context.is_remote = False
    context.trace_flags = 1
    context.trace_state = None

    span.context = context
    span.get_span_context = Mock(return_value=context)

    span.parent = None
    span.kind = SpanKind.SERVER
    span.start_time = int(time.time() * 1e9)
    span.end_time = int(time.time() * 1e9) + 1000000
    span.status = Mock(spec=Status)
    span.status.status_code = StatusCode.OK
    span.status.description = None
    span.attributes = {}
    span.events = []
    span.links = []
    span.resource = Mock()
    span.resource.attributes = {"service.name": "test-service"}
    span.instrumentation_scope = Mock()
    span.instrumentation_scope.name = "test-scope"
    span.instrumentation_scope.version = "1.0.0"
    return span


@pytest.fixture
def mirascope_base_url() -> str:
    """Get Mirascope base URL from environment or return default."""
    load_dotenv()
    return os.getenv("MIRASCOPE_BASE_URL", "http://localhost:3000")


@pytest.fixture
def mirascope_client(mirascope_api_key: str, mirascope_base_url: str) -> Mirascope:
    """Create real Fern-generated client for VCR tests."""
    return get_sync_client(
        api_key=mirascope_api_key,
        base_url=mirascope_base_url,
    )


@pytest.fixture
def otlp_exporter(mirascope_client: Mirascope) -> MirascopeOTLPExporter:
    """Create MirascopeOTLPExporter with transport."""
    return MirascopeOTLPExporter(
        client=mirascope_client, timeout=30.0, max_retry_attempts=3
    )


@pytest.fixture
def batch_processor(otlp_exporter: MirascopeOTLPExporter) -> BatchSpanProcessor:
    """Create BatchSpanProcessor with OTLP exporter."""
    return BatchSpanProcessor(otlp_exporter)


@pytest.fixture
def mirascope_processor(
    otlp_exporter: MirascopeOTLPExporter,
    batch_processor: BatchSpanProcessor,
) -> MirascopeSpanProcessor:
    """Create MirascopeSpanProcessor with both exporters."""
    return MirascopeSpanProcessor(
        otlp_exporter=otlp_exporter,
        batch_processor=batch_processor,
    )
