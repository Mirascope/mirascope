"""Tests for versioning module with tracing attributes."""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import patch

import pytest
from inline_snapshot import snapshot
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from mirascope.ops import ClosureComputationError, session, version
from mirascope.ops._internal.closure import Closure

from .utils import extract_span_data


@pytest.fixture(autouse=True)
def clear_closure_cache() -> Generator[None, None, None]:
    """Ensure Closure.from_fn cache is cleared between tests."""
    Closure.from_fn.cache_clear()
    yield
    Closure.from_fn.cache_clear()


def test_closure_computation_failure() -> None:
    """Ensures `VersionedFunction`s operate like `TracedFunction`s when closure computation fails."""
    with patch(
        "mirascope.ops._internal.closure.Closure.from_fn",
        side_effect=ClosureComputationError(qualified_name="fn"),
    ):

        @version
        def fn() -> str:
            return "ok"

        result = fn()
        assert result == "ok"

        @version
        async def async_fn() -> str:
            return "ok"

        assert async_fn.closure is None


def test_tags_properly_set() -> None:
    """Tests that `tags` are set properly on the versioned function."""

    @version(tags=["proper"])
    def fn() -> None: ...

    assert fn.tags == ("proper",)

    @version(tags=["async"])
    async def async_fn() -> None: ...

    assert async_fn.tags == ("async",)


def test_version_sync(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test @version decorator captures args and result for sync functions."""

    @version
    def multiply(x: int, y: int) -> int:
        return x * y

    result = multiply(5, 7)
    wrapped_result = multiply.wrapped(5, 7)

    assert result == 35
    assert wrapped_result.result == 35

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 2

    span_data = extract_span_data(spans[0])
    assert span_data == snapshot(
        {
            "name": "multiply",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "multiply",
                "mirascope.fn.is_async": False,
                "mirascope.fn.module": "ops.test_versioning",
                "function_hash": extract_span_data(spans[0])["attributes"][
                    "function_hash"
                ],
                "mirascope.trace.arg_types": '{"x":"int","y":"int"}',
                "mirascope.trace.arg_values": '{"x":5,"y":7}',
                "mirascope.trace.output": 35,
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )

    wrapped_span_data = extract_span_data(spans[1])
    assert wrapped_span_data == span_data


@pytest.mark.asyncio
async def test_version_async(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test async versioning functionality."""
    import asyncio

    @version
    async def process_data(data: dict[str, int]) -> dict[str, float]:
        await asyncio.sleep(0.001)
        return {k: float(v * 2) for k, v in data.items()}

    data, expected_processed_data = {"a": 1, "b": 2}, {"a": 2.0, "b": 4.0}
    result = await process_data(data)
    wrapped_result = await process_data.wrapped(data)

    assert result == expected_processed_data
    assert wrapped_result.result == expected_processed_data

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 2

    span_data = extract_span_data(spans[0])
    assert span_data == snapshot(
        {
            "name": "process_data",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "process_data",
                "mirascope.fn.is_async": True,
                "mirascope.fn.module": "ops.test_versioning",
                "function_hash": extract_span_data(spans[0])["attributes"][
                    "function_hash"
                ],
                "mirascope.trace.arg_types": '{"data":"dict[str, int]"}',
                "mirascope.trace.arg_values": '{"data":{"a":1,"b":2}}',
                "mirascope.trace.output": '{"a":2.0,"b":4.0}',
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )

    wrapped_span_data = extract_span_data(spans[1])
    assert wrapped_span_data == span_data


def test_version_with_session(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that @version decorator records session ID from active session."""

    @version
    def compute(x: int) -> int:
        return x * 10

    with session(id="version-session-789"):
        result = compute(3)

    assert result == 30

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data == snapshot(
        {
            "name": "compute",
            "attributes": {
                "mirascope.ops.session.id": "version-session-789",
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "compute",
                "mirascope.fn.module": "ops.test_versioning",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"x":"int"}',
                "mirascope.trace.arg_values": '{"x":3}',
                "mirascope.trace.output": 30,
                "function_hash": span_data["attributes"]["function_hash"],
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.asyncio
async def test_async_version_with_session(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that async @version decorator records session ID from active session."""

    @version
    async def compute(x: int) -> int:
        return x * 20

    with session(id="async-version-session-999"):
        result = await compute(4)

    assert result == 80

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data == snapshot(
        {
            "name": "compute",
            "attributes": {
                "mirascope.ops.session.id": "async-version-session-999",
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "compute",
                "mirascope.fn.module": "ops.test_versioning",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"x":"int"}',
                "mirascope.trace.arg_values": '{"x":4}',
                "mirascope.trace.output": 80,
                "function_hash": span_data["attributes"]["function_hash"],
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


def test_version_wrapped_method(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test @version decorator with .wrapped() method."""

    @version
    def multiply(x: int, y: int) -> int:
        return x * y

    wrapped_result = multiply.wrapped(5, 7)

    assert wrapped_result.result == 35

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data["name"] == "multiply"
    assert span_data["attributes"]["mirascope.trace.output"] == 35


@pytest.mark.asyncio
async def test_async_version_wrapped_method(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test async @version decorator with .wrapped() method."""

    @version
    async def multiply(x: int, y: int) -> int:
        return x * y

    wrapped_result = await multiply.wrapped(5, 7)

    assert wrapped_result.result == 35

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data["name"] == "multiply"
    assert span_data["attributes"]["mirascope.trace.output"] == 35


def test_version_with_function_uuid(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that function_uuid is set on span when _ensure_registration returns a UUID."""

    @version
    def compute(x: int) -> int:
        return x * 2

    with patch.object(compute, "_ensure_registration", return_value="test-uuid-123"):
        result = compute(5)

    assert result == 10

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data["attributes"]["function_uuid"] == "test-uuid-123"


@pytest.mark.asyncio
async def test_async_version_with_function_uuid(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that function_uuid is set on span when async _ensure_registration returns a UUID."""

    @version
    async def compute(x: int) -> int:
        return x * 2

    async def mock_ensure_registration() -> str:
        return "async-test-uuid-456"

    with patch.object(compute, "_ensure_registration", mock_ensure_registration):
        result = await compute(5)

    assert result == 10

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data["attributes"]["function_uuid"] == "async-test-uuid-456"
