"""Tests for `mirascope.ops.tracing`."""

from __future__ import annotations

from typing import Any, TypeVar

import pytest
from inline_snapshot import snapshot
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from mirascope import ops
from mirascope.ops._internal.exporters.utils import format_span_id, format_trace_id

from .utils import extract_span_data

T = TypeVar("T")


def test_sync_trace(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test @trace decorator captures spans for synchronous functions."""

    @ops.trace
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
                "mirascope.fn.module": "ops.test_tracing",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"x":"int","y":"int"}',
                "mirascope.trace.arg_values": '{"x":5,"y":7}',
                "mirascope.trace.output": 35,
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )

    wrapped_span = spans[1]
    context = wrapped_span.get_span_context()
    assert context is not None
    assert wrapped_result.span_id == format_span_id(context.span_id)
    assert wrapped_result.trace_id == format_trace_id(context.trace_id)

    wrapped_span_data = extract_span_data(wrapped_span)
    assert wrapped_span_data == span_data


@pytest.mark.asyncio
async def test_async_trace(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test @trace decorator captures spans for asynchronous functions."""

    @ops.trace
    async def multiply(x: int, y: int) -> int:
        return x * y

    result = await multiply(5, 7)
    wrapped_result = await multiply.wrapped(5, 7)

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
                "mirascope.fn.module": "ops.test_tracing",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"x":"int","y":"int"}',
                "mirascope.trace.arg_values": '{"x":5,"y":7}',
                "mirascope.trace.output": 35,
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )

    wrapped_span = spans[1]
    context = wrapped_span.get_span_context()
    assert context is not None
    assert wrapped_result.span_id == format_span_id(context.span_id)
    assert wrapped_result.trace_id == format_trace_id(context.trace_id)

    wrapped_span_data = extract_span_data(wrapped_span)
    assert wrapped_span_data == span_data


def test_sync_trace_no_return_with_tags(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Tests that synchronous functions set tags properly."""

    @ops.trace(tags=["sync"])
    def tagged() -> None: ...

    tagged()

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert "mirascope.trace.output" not in span_data["attributes"]
    assert "mirascope.trace.tags" in span_data["attributes"]
    assert span_data["attributes"]["mirascope.trace.tags"] == ("sync",)


@pytest.mark.asyncio
async def test_async_trace_no_return_with_tags(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Tests that asynchronous functions set tags properly."""

    @ops.trace(tags=["async"])
    async def tagged() -> None: ...

    await tagged()

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert "mirascope.trace.output" not in span_data["attributes"]
    assert "mirascope.trace.tags" in span_data["attributes"]
    assert span_data["attributes"]["mirascope.trace.tags"] == ("async",)


def test_trace_complex_serialization(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Tests that primitives and non-primitives are properly serialized."""

    class CantSerialize:
        case: str

        def __init__(self, case: str) -> None:
            self.case = case

        def __repr__(self) -> str:
            return f"CantSerialize(case='{self.case}')"

    @ops.trace
    def process(
        json_object: dict[str, str],
        cant_serialize: CantSerialize,
    ) -> CantSerialize:
        return CantSerialize(case="can't serialize output")

    process(
        {"key": "value"},
        CantSerialize(case="can't serialize arg"),
    )

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data == snapshot(
        {
            "name": "process",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "process",
                "mirascope.fn.module": "ops.test_tracing",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"json_object":"dict[str, str]","cant_serialize":"CantSerialize"}',
                "mirascope.trace.arg_values": '{"json_object":{"key":"value"},"cant_serialize":"CantSerialize(case=\'can\'t serialize arg\')"}',
                "mirascope.trace.output": "CantSerialize(case='can't serialize output')",
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


def test_trace_missing_and_dynamic_type_hints(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Tests that @trace properly handles dynamic annotations."""

    def fn(value: Any, other: Any) -> None: ...  # noqa: ANN401

    fn.__annotations__ = {"value": int}
    fn = ops.trace(fn)
    fn(1, "no_type_hint")

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data == snapshot(
        {
            "name": "fn",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "fn",
                "mirascope.fn.module": "ops.test_tracing",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"value":"int","other":"str"}',
                "mirascope.trace.arg_values": '{"value":1,"other":"no_type_hint"}',
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


def test_trace_with_session(span_exporter: InMemorySpanExporter) -> None:
    """Test that @ops.trace decorator records session ID from active session."""

    @ops.trace
    def process(x: int) -> int:
        return x * 2

    with ops.session(id="trace-session-123"):
        result = process(5)

    assert result == 10

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data == snapshot(
        {
            "name": "process",
            "attributes": {
                "mirascope.ops.session.id": "trace-session-123",
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "process",
                "mirascope.fn.module": "ops.test_tracing",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"x":"int"}',
                "mirascope.trace.arg_values": '{"x":5}',
                "mirascope.trace.output": 10,
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.asyncio
async def test_async_trace_with_session(span_exporter: InMemorySpanExporter) -> None:
    """Test that async @trace decorator records session ID from active session."""

    @ops.trace
    async def process(x: int) -> int:
        return x * 3

    with ops.session(id="async-trace-session-456"):
        result = await process(7)

    assert result == 21

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data == snapshot(
        {
            "name": "process",
            "attributes": {
                "mirascope.ops.session.id": "async-trace-session-456",
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "process",
                "mirascope.fn.module": "ops.test_tracing",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"x":"int"}',
                "mirascope.trace.arg_values": '{"x":7}',
                "mirascope.trace.output": 21,
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@ops.trace
def module_level_traced_function(x: int) -> int:
    """Module-level function to test get_qualified_name for non-local functions."""
    return x * 4


def test_trace_module_level_function(span_exporter: InMemorySpanExporter) -> None:
    """Test @trace decorator on module-level functions (non-local function qualname)."""
    result = module_level_traced_function(3)

    assert result == 12

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data == snapshot(
        {
            "name": "module_level_traced_function",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "module_level_traced_function",
                "mirascope.fn.module": "ops.test_tracing",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"x":"int"}',
                "mirascope.trace.arg_values": '{"x":3}',
                "mirascope.trace.output": 12,
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )
