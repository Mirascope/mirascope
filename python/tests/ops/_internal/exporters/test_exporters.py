"""Test MirascopeOTLPExporter functionality including retry logic and error handling."""

from collections.abc import Generator
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock, Mock, patch

import pytest
from inline_snapshot import snapshot
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    SimpleSpanProcessor,
    SpanExportResult,
)
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.id_generator import RandomIdGenerator
from opentelemetry.trace import INVALID_SPAN_CONTEXT, set_tracer_provider
from opentelemetry.util.types import AttributeValue

from mirascope.api.client import Mirascope
from mirascope.ops._internal.exporters.exporters import MirascopeOTLPExporter
from mirascope.ops._internal.exporters.processors import MirascopeSpanProcessor


class UnsupportedAttribute:
    """Represents an attribute type unsupported by OTLP."""

    def __str__(self) -> str:
        return "unsupported"


SpanAttributesDict = dict[str, AttributeValue | UnsupportedAttribute]
ResourceAttributesDict = dict[str, AttributeValue]


@patch("mirascope.ops._internal.exporters.exporters.time.sleep")
def test_retry_on_network_error(mock_sleep: Mock, span: Mock) -> None:
    """Test that export retries on network errors."""
    client = Mock()
    exporter = MirascopeOTLPExporter(client=client, max_retry_attempts=3)

    success_response = Mock()
    success_response.partial_success = None

    client.traces.create = Mock(
        side_effect=[
            Exception("Connection error"),
            Exception("Timeout error"),
            success_response,
        ]
    )

    result = exporter.export([span])

    assert result == snapshot(SpanExportResult.SUCCESS)
    assert client.traces.create.call_count == snapshot(3)
    assert mock_sleep.call_count == snapshot(2)

    sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
    assert sleep_calls == snapshot([0.1, 0.2])


@patch("mirascope.ops._internal.exporters.exporters.time.sleep")
def test_max_retries_exceeded(mock_sleep: Mock, span: Mock) -> None:
    """Test that export fails after max retries exceeded."""
    client = Mock()
    exporter = MirascopeOTLPExporter(client=client, max_retry_attempts=3)

    client.traces.create = Mock(side_effect=Exception("Persistent connection error"))

    result = exporter.export([span])

    assert result == snapshot(SpanExportResult.FAILURE)
    assert client.traces.create.call_count == snapshot(3)


def test_no_retry_on_partial_failure(span: Mock) -> None:
    """Test that export doesn't retry on partial failures (invalid data)."""
    client = Mock()
    exporter = MirascopeOTLPExporter(client=client, max_retry_attempts=3)

    response = Mock()
    response.partial_success = Mock()
    response.partial_success.rejected_spans = 1

    client.traces.create = Mock(return_value=response)

    result = exporter.export([span])

    assert result == snapshot(SpanExportResult.FAILURE)
    assert client.traces.create.call_count == snapshot(1)


def test_immediate_success(span: Mock) -> None:
    """Test that successful export doesn't retry."""
    client = Mock()
    exporter = MirascopeOTLPExporter(client=client, max_retry_attempts=3)

    success_response = Mock()
    success_response.partial_success = None
    client.traces.create = Mock(return_value=success_response)

    result = exporter.export([span])

    assert result == snapshot(SpanExportResult.SUCCESS)
    assert client.traces.create.call_count == snapshot(1)


@patch("mirascope.ops._internal.exporters.exporters.time.sleep")
def test_exponential_backoff_cap(mock_sleep: Mock, span: Mock) -> None:
    """Test that exponential backoff is capped at 5 seconds."""
    client = Mock()
    exporter = MirascopeOTLPExporter(client=client, max_retry_attempts=5)

    success_response = Mock()
    success_response.partial_success = None
    client.traces.create = Mock(
        side_effect=[Exception("Error")] * 4 + [success_response]
    )

    result = exporter.export([span])

    assert result == snapshot(SpanExportResult.SUCCESS)
    assert mock_sleep.call_count == snapshot(4)

    calls = [call[0][0] for call in mock_sleep.call_args_list]
    assert calls == snapshot([0.1, 0.2, 0.4, 0.8])


def test_missing_telemetry_endpoint_returns_failure(span: Mock) -> None:
    """Test that export fails when client doesn't have telemetry endpoint."""
    client = Mock()
    del client.telemetry

    exporter = MirascopeOTLPExporter(client=client, max_retry_attempts=3)

    result = exporter.export([span])

    assert result == snapshot(SpanExportResult.FAILURE)
    assert hasattr(client, "telemetry") == snapshot(False)


def test_empty_spans_still_success() -> None:
    """Test that empty span list returns success without checking endpoint."""
    client = Mock()

    del client.telemetry

    exporter = MirascopeOTLPExporter(client=client)

    result = exporter.export([])

    assert result == snapshot(SpanExportResult.SUCCESS)


@pytest.fixture
def mock_span_ids() -> Generator[None, None, None]:
    """Mock trace and span ID generation for consistent testing."""
    trace_counter = 0
    span_counter = 0

    def generate_trace_id() -> int:
        nonlocal trace_counter
        trace_counter += 1
        return trace_counter

    def generate_span_id() -> int:
        nonlocal span_counter
        span_counter += 1
        return span_counter

    with (
        patch.object(
            RandomIdGenerator, "generate_trace_id", side_effect=generate_trace_id
        ),
        patch.object(
            RandomIdGenerator, "generate_span_id", side_effect=generate_span_id
        ),
    ):
        yield


@pytest.fixture
def resource() -> Resource:
    """Create a test resource."""
    return Resource.create({"service.name": "test-service"})


@pytest.fixture
def provider_with_memory_exporter(
    resource: Resource, mock_span_ids: None
) -> tuple[TracerProvider, InMemorySpanExporter]:
    """Create TracerProvider with InMemorySpanExporter."""

    provider = TracerProvider(resource=resource, id_generator=RandomIdGenerator())
    memory_exporter = InMemorySpanExporter()
    processor = SimpleSpanProcessor(memory_exporter)
    provider.add_span_processor(processor)

    return provider, memory_exporter


def test_transport_export_single_span(
    mirascope_client: Mirascope,
    provider_with_memory_exporter: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """Test exporting a single span with real client."""
    mirascope_client.traces.create = MagicMock(return_value=None)

    otlp_exporter = MirascopeOTLPExporter(
        client=mirascope_client,
        timeout=30.0,
        max_retry_attempts=3,
    )

    provider, memory_exporter = provider_with_memory_exporter
    tracer = provider.get_tracer("test-tracer", "1.0.0")

    with tracer.start_as_current_span("test-operation") as span:
        span.set_attribute("test.key", "test-value")
        span.set_attribute("float", 1.0)
        span.set_attribute("sequence", ["a", "b"])

    provider.force_flush()
    spans = memory_exporter.get_finished_spans()

    result = otlp_exporter.export(spans)
    assert result == SpanExportResult.SUCCESS

    mirascope_client.traces.create.assert_called_once()
    sent_data = mirascope_client.traces.create.call_args[1]["resource_spans"]
    assert len(sent_data) == 1
    assert sent_data[0].scope_spans is not None
    assert len(sent_data[0].scope_spans) == 1
    assert len(sent_data[0].scope_spans[0].spans) == 1
    assert sent_data[0].scope_spans[0].spans[0].name == "test-operation"


def test_transport_export_batch(
    mirascope_client: Mirascope,
    provider_with_memory_exporter: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """Test exporting multiple spans in a batch."""
    mirascope_client.traces.create = MagicMock(return_value=None)

    otlp_exporter = MirascopeOTLPExporter(
        client=mirascope_client,
        timeout=30.0,
        max_retry_attempts=3,
    )

    provider, memory_exporter = provider_with_memory_exporter
    tracer = provider.get_tracer("batch-tracer")

    for index in range(3):
        with tracer.start_as_current_span(f"operation-{index}") as span:
            span.set_attribute("index", index)

    provider.force_flush()
    spans = memory_exporter.get_finished_spans()

    result = otlp_exporter.export(spans)
    assert result == SpanExportResult.SUCCESS

    mirascope_client.traces.create.assert_called_once()
    sent_data = mirascope_client.traces.create.call_args[1]["resource_spans"]
    assert len(sent_data) == 1
    assert sent_data[0].scope_spans is not None
    assert len(sent_data[0].scope_spans) == 1
    assert len(sent_data[0].scope_spans[0].spans) == 3


def test_immediate_start_exporter(
    mirascope_client: Mirascope,
    provider_with_memory_exporter: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """Test ImmediateStartExporter with real client."""
    mirascope_client.traces.create = MagicMock(return_value=None)

    otlp_exporter = MirascopeOTLPExporter(
        client=mirascope_client, timeout=30.0, max_retry_attempts=2
    )

    provider, memory_exporter = provider_with_memory_exporter
    tracer = provider.get_tracer("start-tracer", "1.0.0")

    with tracer.start_as_current_span("start-event-test") as span:
        span.set_attribute("event.type", "start")

    provider.force_flush()
    spans = memory_exporter.get_finished_spans()

    if spans:
        result = otlp_exporter.export([spans[0]])
        assert result == SpanExportResult.SUCCESS

        mirascope_client.traces.create.assert_called_once()
        sent_data = mirascope_client.traces.create.call_args[1]["resource_spans"]
        assert len(sent_data) == 1


def test_otlp_exporter(
    mirascope_client: Mirascope,
    provider_with_memory_exporter: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """Test MirascopeOTLPExporter with real client."""
    mirascope_client.traces.create = MagicMock(return_value=None)

    otlp_exporter = MirascopeOTLPExporter(client=mirascope_client, timeout=30.0)

    provider, memory_exporter = provider_with_memory_exporter
    tracer = provider.get_tracer("otlp-tracer", "2.0.0")

    for index in range(2):
        with tracer.start_as_current_span(f"otlp-span-{index}") as span:
            span.set_attribute("otlp.test", True)
            span.set_attribute("index", index)

    provider.force_flush()
    spans = memory_exporter.get_finished_spans()

    result = otlp_exporter.export(spans)
    assert result == SpanExportResult.SUCCESS

    mirascope_client.traces.create.assert_called_once()
    sent_data = mirascope_client.traces.create.call_args[1]["resource_spans"]
    assert len(sent_data) == 1
    assert sent_data[0].scope_spans is not None
    assert len(sent_data[0].scope_spans[0].spans) == 2


def test_full_pipeline(
    mirascope_client: Mirascope,
    mock_span_ids: None,
) -> None:
    """Test complete pipeline with two-phase export."""
    mirascope_client.traces.create = MagicMock(return_value=None)

    otlp_exporter = MirascopeOTLPExporter(
        client=mirascope_client,
        timeout=30.0,
        max_retry_attempts=3,
    )

    batch_processor = BatchSpanProcessor(
        span_exporter=otlp_exporter,
        max_queue_size=2048,
        schedule_delay_millis=5000,
        export_timeout_millis=30000,
        max_export_batch_size=512,
    )

    executor = ThreadPoolExecutor(
        max_workers=2,
        thread_name_prefix="mirascope-span-processor",
    )

    processor = MirascopeSpanProcessor(
        otlp_exporter=otlp_exporter,
        batch_processor=batch_processor,
        executor=executor,
    )

    provider = TracerProvider(id_generator=RandomIdGenerator())
    provider.add_span_processor(processor)
    set_tracer_provider(provider)

    tracer = provider.get_tracer("full-pipeline-tracer", "1.0.0")

    with tracer.start_as_current_span("parent-operation") as parent:
        parent.set_attribute("operation.type", "parent")
        parent.set_attribute("test.framework", "pytest")

        with tracer.start_as_current_span("child-operation-1") as child1:
            child1.set_attribute("operation.type", "child")
            child1.set_attribute("child.index", 1)

        with tracer.start_as_current_span("child-operation-2") as child2:
            child2.set_attribute("operation.type", "child")
            child2.set_attribute("child.index", 2)

    processor.force_flush(timeout_millis=30000)

    provider.shutdown()

    assert mirascope_client.traces.create.call_count >= snapshot(4)


def test_spans_with_invalid_context_are_skipped(
    mirascope_client: Mirascope,
) -> None:
    """Tests that the exporter skips any spans that do not have a valid context."""
    mirascope_client.traces.create = MagicMock(return_value=None)
    exporter = MirascopeOTLPExporter(client=mirascope_client)

    invalid_span = ReadableSpan(name="invalid", context=INVALID_SPAN_CONTEXT)

    result = exporter.export([invalid_span])
    assert result == snapshot(SpanExportResult.SUCCESS)
    mirascope_client.traces.create.assert_called_once_with(resource_spans=[])


def test_export_with_various_resource_attribute_types(
    mirascope_client: Mirascope,
    mock_span_ids: None,
) -> None:
    """Test exporting spans with various resource attribute types (bool, int, float, sequence)."""
    mirascope_client.traces.create = MagicMock(return_value=None)

    resource = Resource.create(
        {
            "service.name": "test-service",
            "service.enabled": True,
            "service.instance.count": 42,
            "service.load": 3.14,
            "service.tags": ["tag1", "tag2"],
        }
    )

    provider = TracerProvider(resource=resource, id_generator=RandomIdGenerator())
    memory_exporter = InMemorySpanExporter()
    processor = SimpleSpanProcessor(memory_exporter)
    provider.add_span_processor(processor)

    otlp_exporter = MirascopeOTLPExporter(client=mirascope_client)

    tracer = provider.get_tracer("resource-test-tracer")
    with tracer.start_as_current_span("resource-test-span"):
        pass

    provider.force_flush()
    spans = memory_exporter.get_finished_spans()

    result = otlp_exporter.export(spans)
    assert result == SpanExportResult.SUCCESS

    mirascope_client.traces.create.assert_called_once()
    sent_data = mirascope_client.traces.create.call_args[1]["resource_spans"]
    assert len(sent_data) == 1

    resource_attrs = {
        attr.key: (
            attr.value.string_value
            or attr.value.bool_value
            or attr.value.int_value
            or attr.value.double_value
        )
        for attr in sent_data[0].resource.attributes
    }

    assert resource_attrs == snapshot(
        {
            "telemetry.sdk.language": "python",
            "telemetry.sdk.name": "opentelemetry",
            "telemetry.sdk.version": "1.38.0",
            "service.name": "test-service",
            "service.enabled": True,
            "service.instance.count": "42",
            "service.load": 3.14,
            "service.tags": "['tag1', 'tag2']",
        }
    )


def test_export_after_shutdown_returns_failure(span: Mock) -> None:
    """Test that export returns FAILURE after shutdown is called."""
    client = Mock()
    exporter = MirascopeOTLPExporter(client=client)

    exporter.shutdown()

    result = exporter.export([span])
    assert result == SpanExportResult.FAILURE
    client.traces.create.assert_not_called()


def test_force_flush_returns_true() -> None:
    """Test that force_flush always returns True."""
    client = Mock()
    exporter = MirascopeOTLPExporter(client=client)

    assert exporter.force_flush() is True
    assert exporter.force_flush(timeout_millis=1000) is True
