"""Unit tests for MirascopeSpanProcessor focusing on interface behavior."""

from concurrent.futures import Future, ThreadPoolExecutor
from unittest.mock import Mock

import pytest
from inline_snapshot import snapshot
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from mirascope.ops._internal.exporters import (
    MirascopeOTLPExporter,
    MirascopeSpanProcessor,
)

from .utils import create_mock_span


@pytest.fixture
def mock_span() -> Mock:
    """Create a mock span for processor tests."""
    return create_mock_span()


@pytest.fixture
def mock_spans() -> list[Mock]:
    """Create multiple mock spans for processor tests."""
    shared_resource = Mock(attributes={"service.name": "test-service"})
    return [
        create_mock_span(
            name=f"test-span-{index}",
            span_id=0x1234567890ABCDE0 + index,
            shared_resource=shared_resource,
        )
        for index in range(3)
    ]


def test_processor_sends_start_events_immediately(
    otlp_exporter: MirascopeOTLPExporter,
    batch_processor: BatchSpanProcessor,
    mock_span: Mock,
) -> None:
    """Test that processor sends start events immediately when spans start."""
    otlp_exporter.export = Mock(return_value=True)
    processor = MirascopeSpanProcessor(
        otlp_exporter=otlp_exporter,
        batch_processor=batch_processor,
    )

    processor.on_start(mock_span)
    processor.shutdown()

    assert otlp_exporter.export.call_count == snapshot(1)
    otlp_exporter.export.assert_called_once_with([mock_span])


def test_processor_batches_end_events(
    otlp_exporter: MirascopeOTLPExporter,
    batch_processor: BatchSpanProcessor,
    mock_spans: list[Mock],
) -> None:
    """Test that processor batches end events through batch processor."""
    batch_processor.on_end = Mock()
    processor = MirascopeSpanProcessor(
        otlp_exporter=otlp_exporter,
        batch_processor=batch_processor,
    )

    for span in mock_spans:
        processor.on_end(span)

    assert batch_processor.on_end.call_count == snapshot(3)
    for span in mock_spans:
        batch_processor.on_end.assert_any_call(span)


def test_processor_handles_concurrent_spans(
    otlp_exporter: MirascopeOTLPExporter,
    batch_processor: BatchSpanProcessor,
    mock_spans: list[Mock],
) -> None:
    """Test that processor correctly handles concurrent span operations."""
    otlp_exporter.export = Mock(return_value=True)
    batch_processor.on_end = Mock()
    processor = MirascopeSpanProcessor(
        otlp_exporter=otlp_exporter,
        batch_processor=batch_processor,
    )

    for span in mock_spans:
        processor.on_start(span)
        processor.on_end(span)

    processor.shutdown()

    assert otlp_exporter.export.call_count == snapshot(3)
    assert batch_processor.on_end.call_count == snapshot(3)


def test_processor_graceful_shutdown(
    otlp_exporter: MirascopeOTLPExporter,
    batch_processor: BatchSpanProcessor,
    mock_span: Mock,
) -> None:
    """Test that processor shuts down gracefully and completes pending work."""
    otlp_exporter.export = Mock(return_value=True)
    otlp_exporter.shutdown = Mock()
    batch_processor.shutdown = Mock()

    processor = MirascopeSpanProcessor(
        otlp_exporter=otlp_exporter,
        batch_processor=batch_processor,
    )

    processor.on_start(mock_span)
    processor.shutdown()

    assert otlp_exporter.shutdown.call_count == snapshot(1)
    assert batch_processor.shutdown.call_count == snapshot(1)
    assert otlp_exporter.export.call_count == snapshot(1)
    otlp_exporter.export.assert_called_once_with([mock_span])


def test_processor_force_flush_completes_pending_work(
    otlp_exporter: MirascopeOTLPExporter,
    batch_processor: BatchSpanProcessor,
    mock_spans: list[Mock],
) -> None:
    """Test that force flush completes all pending work."""
    batch_processor.force_flush = Mock(return_value=True)
    processor = MirascopeSpanProcessor(
        otlp_exporter=otlp_exporter,
        batch_processor=batch_processor,
    )

    for span in mock_spans:
        processor.on_end(span)

    result = processor.force_flush(timeout_millis=5000)

    assert result == snapshot(True)
    assert batch_processor.force_flush.call_count == snapshot(1)
    batch_processor.force_flush.assert_called_once_with(5000)


def test_processor_works_without_batch_processor(
    otlp_exporter: MirascopeOTLPExporter,
    mock_span: Mock,
) -> None:
    """Test that processor works correctly without batch processor (start-only mode)."""
    otlp_exporter.export = Mock(return_value=True)
    processor = MirascopeSpanProcessor(
        otlp_exporter=otlp_exporter,
        batch_processor=None,
    )

    processor.on_start(mock_span)
    processor.on_end(mock_span)
    result = processor.force_flush()
    processor.shutdown()

    assert otlp_exporter.export.call_count == snapshot(1)
    otlp_exporter.export.assert_called_once_with([mock_span])
    assert result == snapshot(True)


def test_processor_ignores_operations_after_shutdown(
    otlp_exporter: MirascopeOTLPExporter,
    batch_processor: BatchSpanProcessor,
    mock_span: Mock,
) -> None:
    """Test that processor ignores operations after shutdown."""
    otlp_exporter.export = Mock(return_value=True)
    batch_processor.on_end = Mock()
    processor = MirascopeSpanProcessor(
        otlp_exporter=otlp_exporter,
        batch_processor=batch_processor,
    )

    processor.shutdown()
    processor.on_start(mock_span)
    processor.on_end(mock_span)

    assert otlp_exporter.export.call_count == snapshot(0)
    assert batch_processor.on_end.call_count == snapshot(0)


def test_processor_with_custom_executor(
    otlp_exporter: MirascopeOTLPExporter,
    batch_processor: BatchSpanProcessor,
    mock_span: Mock,
) -> None:
    """Test that processor works with custom executor."""
    custom_executor = ThreadPoolExecutor(max_workers=5)
    custom_executor.submit = Mock(return_value=Mock(spec=Future))

    processor = MirascopeSpanProcessor(
        otlp_exporter=otlp_exporter,
        batch_processor=batch_processor,
        executor=custom_executor,
    )

    processor.on_start(mock_span)

    assert custom_executor.submit.call_count == snapshot(1)
    call_args = custom_executor.submit.call_args[0]
    assert call_args[0] == otlp_exporter.export
    assert call_args[1][0] == mock_span

    processor.shutdown()
