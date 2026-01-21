"""Tests for `mirascope.ops.tracing`."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any, TypeVar
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from inline_snapshot import snapshot
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from mirascope import llm, ops
from mirascope.ops._internal.exporters.utils import format_span_id, format_trace_id

from ..utils import extract_span_data

T = TypeVar("T")


@pytest.fixture(autouse=True, scope="function")
def initialize(tracer_provider: TracerProvider) -> Generator[None, None, None]:
    """Initialize ops configuration and LLM instrumentation for each test."""
    ops.configure(tracer_provider=tracer_provider)
    ops.instrument_llm()
    yield
    ops.uninstrument_llm()


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
                "mirascope.fn.module": "ops._internal.test_tracing",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"x":"int","y":"int"}',
                "mirascope.trace.arg_values": '{"x":5,"y":7}',
                "mirascope.trace.output": 35,
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )

    traced_span = spans[1]
    traced_context = traced_span.get_span_context()
    assert traced_context is not None
    assert wrapped_result.span_id == format_span_id(traced_context.span_id)
    assert wrapped_result.trace_id == format_trace_id(traced_context.trace_id)

    call_span = spans[1]
    call_span_data = extract_span_data(call_span)
    assert call_span_data == span_data


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
                "mirascope.fn.module": "ops._internal.test_tracing",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"x":"int","y":"int"}',
                "mirascope.trace.arg_values": '{"x":5,"y":7}',
                "mirascope.trace.output": 35,
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )

    traced_span = spans[1]
    traced_context = traced_span.get_span_context()
    assert traced_context is not None
    assert wrapped_result.span_id == format_span_id(traced_context.span_id)
    assert wrapped_result.trace_id == format_trace_id(traced_context.trace_id)

    call_span = spans[1]
    call_span_data = extract_span_data(call_span)
    assert call_span_data == span_data


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
                "mirascope.fn.module": "ops._internal.test_tracing",
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
    traced_fn = ops.trace(fn)
    traced_fn(1, "no_type_hint")

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data == snapshot(
        {
            "name": "fn",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "fn",
                "mirascope.fn.module": "ops._internal.test_tracing",
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
        wrapped_result = process.wrapped(5)

    assert wrapped_result.result == 10

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
                "mirascope.fn.module": "ops._internal.test_tracing",
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
        wrapped_result = await process.wrapped(7)

    assert wrapped_result.result == 21

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
                "mirascope.fn.module": "ops._internal.test_tracing",
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
    wrapped_result = module_level_traced_function.wrapped(3)

    assert wrapped_result.result == 12

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data == snapshot(
        {
            "name": "module_level_traced_function",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "module_level_traced_function",
                "mirascope.fn.module": "ops._internal.test_tracing",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"x":"int"}',
                "mirascope.trace.arg_values": '{"x":3}',
                "mirascope.trace.output": 12,
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
def test_traced_call_sync(span_exporter: InMemorySpanExporter) -> None:
    """Test @ops.trace on @llm.call creates TracedCall and returns Response directly."""

    @ops.trace
    @llm.call("openai/gpt-4o-mini")
    def recommend(genre: str) -> str:
        return f"Recommend a {genre} book."

    assert isinstance(recommend, ops.TracedCall)

    response = recommend("fantasy")
    assert response.content

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend.call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend.call",
                "mirascope.fn.module": "ops._internal.test_tracing",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"genre":"str"}',
                "mirascope.trace.arg_values": '{"genre":"fantasy"}',
                "mirascope.response.provider_id": "openai",
                "mirascope.response.model_id": "openai/gpt-4o-mini",
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"Recommend a fantasy book."}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"I recommend **\\"The Name of the Wind\\"** by Patrick Rothfuss. It\'s the first book in the *Kingkiller Chronicle* series and follows the story of Kvothe, a gifted young man who grows into a legendary figure. The book beautifully blends magic, music, and storytelling, offering a rich and immersive world. If you enjoy character-driven narratives with a touch of mystery and adventure, this is a great choice!"}]',
                "mirascope.response.usage": '{"input_tokens":12,"output_tokens":87,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":99}',
                "mirascope.trace.output": 'I recommend **"The Name of the Wind"** by Patrick Rothfuss. It\'s the first book in the *Kingkiller Chronicle* series and follows the story of Kvothe, a gifted young man who grows into a legendary figure. The book beautifully blends magic, music, and storytelling, offering a rich and immersive world. If you enjoy character-driven narratives with a touch of mystery and adventure, this is a great choice!',
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
def test_traced_call_wrapped_method(span_exporter: InMemorySpanExporter) -> None:
    """Test TracedCall.wrapped() returns Trace."""

    @ops.trace
    @llm.call("openai/gpt-4o-mini")
    def recommend(genre: str) -> str:
        return f"Recommend a {genre} book."

    trace = recommend.wrapped("mystery")
    assert trace.result.content
    assert trace.span_id is not None

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend.call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend.call",
                "mirascope.fn.module": "ops._internal.test_tracing",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"genre":"str"}',
                "mirascope.trace.arg_values": '{"genre":"mystery"}',
                "mirascope.response.provider_id": "openai",
                "mirascope.response.model_id": "openai/gpt-4o-mini",
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"Recommend a mystery book."}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"I recommend \\"The Girl with the Dragon Tattoo\\" by Stieg Larsson. This gripping mystery follows journalist Mikael Blomkvist and hacker Lisbeth Salander as they investigate a decades-old disappearance in a wealthy family. The novel expertly weaves elements of suspense, intrigue, and rich character development. It\'s the first in the \\"Millennium\\" series, so if you enjoy it, there\'s more to explore!"}]',
                "mirascope.response.usage": '{"input_tokens":12,"output_tokens":84,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":96}',
                "mirascope.trace.output": 'I recommend "The Girl with the Dragon Tattoo" by Stieg Larsson. This gripping mystery follows journalist Mikael Blomkvist and hacker Lisbeth Salander as they investigate a decades-old disappearance in a wealthy family. The novel expertly weaves elements of suspense, intrigue, and rich character development. It\'s the first in the "Millennium" series, so if you enjoy it, there\'s more to explore!',
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
def test_traced_call_wrapped_call_method(span_exporter: InMemorySpanExporter) -> None:
    """Test TracedCall.wrapped.call() returns Response directly (bypassing Trace)."""

    @ops.trace
    @llm.call("openai/gpt-4o-mini")
    def recommend(genre: str) -> str:
        return f"Recommend a {genre} book."

    response = recommend("scifi")
    assert response.content
    assert hasattr(response, "content")
    assert not hasattr(response, "span_id")

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend.call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend.call",
                "mirascope.fn.module": "ops._internal.test_tracing",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"genre":"str"}',
                "mirascope.trace.arg_values": '{"genre":"scifi"}',
                "mirascope.response.provider_id": "openai",
                "mirascope.response.model_id": "openai/gpt-4o-mini",
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"Recommend a scifi book."}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"I recommend **\\"Dune\\" by Frank Herbert**. It\'s a classic of science fiction, set on the desert planet of Arrakis, where precious resources and political intrigue shape the fate of its inhabitants. The themes of ecology, religion, and power make it a richly layered read. If you enjoy intricate world-building and deep philosophical questions, this book is a must-read!"}]',
                "mirascope.response.usage": '{"input_tokens":13,"output_tokens":76,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":89}',
                "mirascope.trace.output": 'I recommend **"Dune" by Frank Herbert**. It\'s a classic of science fiction, set on the desert planet of Arrakis, where precious resources and political intrigue shape the fate of its inhabitants. The themes of ecology, religion, and power make it a richly layered read. If you enjoy intricate world-building and deep philosophical questions, this book is a must-read!',
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
def test_traced_call_wrapped_stream(span_exporter: InMemorySpanExporter) -> None:
    """Test TracedCall.wrapped_stream() returns Trace[StreamResponse]."""

    @ops.trace
    @llm.call("openai/gpt-4o-mini")
    def recommend(genre: str) -> str:
        return f"Recommend a {genre} book."

    trace = recommend.wrapped_stream("adventure")
    assert trace.span_id is not None
    trace.result.finish()
    assert trace.result.content

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend.stream",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend.stream",
                "mirascope.fn.module": "ops._internal.test_tracing",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"genre":"str"}',
                "mirascope.trace.arg_values": '{"genre":"adventure"}',
                "mirascope.response.provider_id": "openai",
                "mirascope.response.model_id": "openai/gpt-4o-mini",
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"Recommend a adventure book."}],"name":null}]',
                "mirascope.response.content": "[]",
                "mirascope.trace.output": "",
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
def test_traced_call_call_method(span_exporter: InMemorySpanExporter) -> None:
    """Test TracedCall.call() returns Response directly and creates span."""

    @ops.trace
    @llm.call("openai/gpt-4o-mini")
    def recommend(genre: str) -> str:
        return f"Recommend a {genre} book."

    response = recommend.call("fantasy")
    assert response.content

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend.call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend.call",
                "mirascope.fn.module": "ops._internal.test_tracing",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"genre":"str"}',
                "mirascope.trace.arg_values": '{"genre":"fantasy"}',
                "mirascope.response.provider_id": "openai",
                "mirascope.response.model_id": "openai/gpt-4o-mini",
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"Recommend a fantasy book."}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"I recommend **\\"The Name of the Wind\\"** by Patrick Rothfuss. It\'s the first book in the *Kingkiller Chronicle* series and follows the story of Kvothe, a gifted young man who grows into a legendary figure. The narrative blends magic, music, and adventure, all while featuring rich world-building and intricate character development. It\'s a compelling read for any fantasy enthusiast!"}]',
                "mirascope.response.usage": '{"input_tokens":12,"output_tokens":79,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":91}',
                "mirascope.trace.output": "I recommend **\"The Name of the Wind\"** by Patrick Rothfuss. It's the first book in the *Kingkiller Chronicle* series and follows the story of Kvothe, a gifted young man who grows into a legendary figure. The narrative blends magic, music, and adventure, all while featuring rich world-building and intricate character development. It's a compelling read for any fantasy enthusiast!",
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
def test_traced_call_stream_method(span_exporter: InMemorySpanExporter) -> None:
    """Test TracedCall.stream() returns StreamResponse directly and creates span."""

    @ops.trace
    @llm.call("openai/gpt-4o-mini")
    def recommend(genre: str) -> str:
        return f"Recommend a {genre} book."

    stream_response = recommend.wrapped_stream("adventure").result
    stream_response.finish()
    assert stream_response.content

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend.stream",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend.stream",
                "mirascope.fn.module": "ops._internal.test_tracing",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"genre":"str"}',
                "mirascope.trace.arg_values": '{"genre":"adventure"}',
                "mirascope.response.provider_id": "openai",
                "mirascope.response.model_id": "openai/gpt-4o-mini",
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"Recommend a adventure book."}],"name":null}]',
                "mirascope.response.content": "[]",
                "mirascope.trace.output": "",
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_traced_async_call_call_method(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test TracedAsyncCall.call() returns AsyncResponse directly and creates span."""

    @ops.trace
    @llm.call("openai/gpt-4o-mini")
    async def recommend(genre: str) -> str:
        return f"Recommend a {genre} book."

    response = await recommend.call("horror")
    assert response.content

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend.call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend.call",
                "mirascope.fn.module": "ops._internal.test_tracing",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"genre":"str"}',
                "mirascope.trace.arg_values": '{"genre":"horror"}',
                "mirascope.response.provider_id": "openai",
                "mirascope.response.model_id": "openai/gpt-4o-mini",
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"Recommend a horror book."}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"I highly recommend **\\"The Cabin at the End of the World\\" by Paul Tremblay**. It blends psychological horror with existential themes, exploring family dynamics and the impact of fear on human behavior. The tension builds as a family vacation turns into a nightmare when they are confronted by strangers with a terrifying ultimatum. It’s a gripping read that will keep you on the edge of your seat!"}]',
                "mirascope.response.usage": '{"input_tokens":12,"output_tokens":81,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":93}',
                "mirascope.trace.output": 'I highly recommend **"The Cabin at the End of the World" by Paul Tremblay**. It blends psychological horror with existential themes, exploring family dynamics and the impact of fear on human behavior. The tension builds as a family vacation turns into a nightmare when they are confronted by strangers with a terrifying ultimatum. It’s a gripping read that will keep you on the edge of your seat!',
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_traced_async_call_wrapped_method(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test TracedAsyncCall.wrapped() returns AsyncTrace[AsyncResponse] and creates span."""

    @ops.trace
    @llm.call("openai/gpt-4o-mini")
    async def recommend(genre: str) -> str:
        return f"Recommend a {genre} book."

    response = await recommend.wrapped("horror")
    assert response.result.content

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend.call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend.call",
                "mirascope.fn.module": "ops._internal.test_tracing",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"genre":"str"}',
                "mirascope.trace.arg_values": '{"genre":"horror"}',
                "mirascope.response.provider_id": "openai",
                "mirascope.response.model_id": "openai/gpt-4o-mini",
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"Recommend a horror book."}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"I recommend **\\"The Haunting of Hill House\\" by Shirley Jackson**. It\'s a classic psychological horror novel that explores the unsettling experiences of a group of people invited to a supposedly haunted mansion. The atmosphere is eerie, and Jackson expertly delves into themes of fear, isolation, and the unknown. It\'s a must-read for any horror fan!"}]',
                "mirascope.response.usage": '{"input_tokens":12,"output_tokens":70,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":82}',
                "mirascope.trace.output": "I recommend **\"The Haunting of Hill House\" by Shirley Jackson**. It's a classic psychological horror novel that explores the unsettling experiences of a group of people invited to a supposedly haunted mansion. The atmosphere is eerie, and Jackson expertly delves into themes of fear, isolation, and the unknown. It's a must-read for any horror fan!",
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_traced_async_call_stream_method(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test TracedAsyncCall.stream() returns AsyncStreamResponse directly and creates span."""

    @ops.trace
    @llm.call("openai/gpt-4o-mini")
    async def recommend(genre: str) -> str:
        return f"Recommend a {genre} book."

    stream_response = (await recommend.wrapped_stream("adventure")).result
    await stream_response.finish()
    assert stream_response.content

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend.stream",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend.stream",
                "mirascope.fn.module": "ops._internal.test_tracing",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"genre":"str"}',
                "mirascope.trace.arg_values": '{"genre":"adventure"}',
                "mirascope.response.provider_id": "openai",
                "mirascope.response.model_id": "openai/gpt-4o-mini",
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"Recommend a adventure book."}],"name":null}]',
                "mirascope.response.content": "[]",
                "mirascope.trace.output": "",
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
def test_traced_context_call_call_method(span_exporter: InMemorySpanExporter) -> None:
    """Test TracedContextCall.call() returns ContextResponse directly and creates span."""

    @ops.trace
    @llm.call("openai/gpt-4o-mini")
    def recommend(ctx: llm.Context[str], genre: str) -> str:
        return f"{ctx.deps} Recommend a {genre} book."

    ctx = llm.Context(deps="As a librarian,")
    response = recommend.call(ctx, "fantasy")
    assert response.content

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend.call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend.call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"ctx":"llm.Context[str]","genre":"str"}',
                "mirascope.trace.arg_values": '{"ctx":{"deps":"As a librarian,"},"genre":"fantasy"}',
                "mirascope.response.provider_id": "openai",
                "mirascope.response.model_id": "openai/gpt-4o-mini",
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"As a librarian, Recommend a fantasy book."}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"I recommend \\"The Name of the Wind\\" by Patrick Rothfuss. It\'s the first book in the *Kingkiller Chronicle* series and follows the story of Kvothe, an exceptional young man with a mysterious past. The narrative blends magic, music, and adventure, while its lyrical prose and rich world-building immerse readers in an enchanting realm. The character development and storytelling are particularly compelling. Perfect for anyone looking to dive into a captivating fantasy world!"}]',
                "mirascope.response.usage": '{"input_tokens":16,"output_tokens":91,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":107}',
                "mirascope.trace.output": 'I recommend "The Name of the Wind" by Patrick Rothfuss. It\'s the first book in the *Kingkiller Chronicle* series and follows the story of Kvothe, an exceptional young man with a mysterious past. The narrative blends magic, music, and adventure, while its lyrical prose and rich world-building immerse readers in an enchanting realm. The character development and storytelling are particularly compelling. Perfect for anyone looking to dive into a captivating fantasy world!',
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
def test_traced_context_call_wrapped_returns_trace(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test TracedContextCall.wrapped() returns Trace[ContextResponse] (not just result)."""

    @ops.trace
    @llm.call("openai/gpt-4o-mini")
    def recommend(ctx: llm.Context[str], genre: str) -> str:
        return f"{ctx.deps} Recommend a {genre} book."

    ctx = llm.Context(deps="As a librarian,")
    trace = recommend.wrapped(ctx, "biography")
    assert trace.result.content
    assert trace.span_id is not None


@pytest.mark.vcr()
def test_traced_context_call_stream_method(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test TracedContextCall.stream() returns ContextStreamResponse directly and creates span."""

    @ops.trace
    @llm.call("openai/gpt-4o-mini")
    def recommend(ctx: llm.Context[str], genre: str) -> str:
        return f"{ctx.deps} Recommend a {genre} book."

    ctx = llm.Context(deps="As a librarian,")
    stream_response = recommend.wrapped_stream(ctx, "adventure").result
    stream_response.finish()
    assert stream_response.content

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend.stream",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend.stream",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"ctx":"llm.Context[str]","genre":"str"}',
                "mirascope.trace.arg_values": '{"ctx":{"deps":"As a librarian,"},"genre":"adventure"}',
                "mirascope.response.provider_id": "openai",
                "mirascope.response.model_id": "openai/gpt-4o-mini",
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"As a librarian, Recommend a adventure book."}],"name":null}]',
                "mirascope.response.content": "[]",
                "mirascope.trace.output": "",
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_traced_async_context_call_call_method(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test TracedAsyncContextCall.call() returns AsyncContextResponse directly and creates span."""

    @ops.trace
    @llm.call("openai/gpt-4o-mini")
    async def recommend(ctx: llm.Context[str], genre: str) -> str:
        return f"{ctx.deps} Recommend a {genre} book."

    ctx = llm.Context(deps="As a librarian,")
    response = await recommend.call(ctx, "mystery")
    assert response.content

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend.call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend.call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"ctx":"llm.Context[str]","genre":"str"}',
                "mirascope.trace.arg_values": '{"ctx":{"deps":"As a librarian,"},"genre":"mystery"}',
                "mirascope.response.provider_id": "openai",
                "mirascope.response.model_id": "openai/gpt-4o-mini",
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"As a librarian, Recommend a mystery book."}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"I highly recommend **\\"The No. 1 Ladies\' Detective Agency\\" by Alexander McCall Smith**. This charming mystery features Precious Ramotswe, Botswana\'s first female detective, as she navigates various cases with her unique perspective and keen intuition. The book blends humor, culture, and intriguing mysteries, making it a delightful read for both mystery enthusiasts and those looking for something different. It’s the first in a series, so if you enjoy it, there’s plenty more to explore!"}]',
                "mirascope.response.usage": '{"input_tokens":16,"output_tokens":100,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":116}',
                "mirascope.trace.output": "I highly recommend **\"The No. 1 Ladies' Detective Agency\" by Alexander McCall Smith**. This charming mystery features Precious Ramotswe, Botswana's first female detective, as she navigates various cases with her unique perspective and keen intuition. The book blends humor, culture, and intriguing mysteries, making it a delightful read for both mystery enthusiasts and those looking for something different. It’s the first in a series, so if you enjoy it, there’s plenty more to explore!",
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_traced_async_context_call_wrapped_returns_trace(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test TracedAsyncContextCall.wrapped() returns AsyncTrace[AsyncContextResponse] (not just result)."""

    @ops.trace
    @llm.call("openai/gpt-4o-mini")
    async def recommend(ctx: llm.Context[str], genre: str) -> str:
        return f"{ctx.deps} Recommend a {genre} book."

    ctx = llm.Context(deps="As a librarian,")
    trace = await recommend.wrapped(ctx, "biography")
    assert trace.result.content
    assert trace.span_id is not None


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_traced_async_context_call_stream_method(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test TracedAsyncContextCall.stream() returns AsyncContextStreamResponse directly and creates span."""

    @ops.trace
    @llm.call("openai/gpt-4o-mini")
    async def recommend(ctx: llm.Context[str], genre: str) -> str:
        return f"{ctx.deps} Recommend a {genre} book."

    ctx = llm.Context(deps="As a librarian,")
    stream_response = (await recommend.wrapped_stream(ctx, "adventure")).result
    await stream_response.finish()
    assert stream_response.content

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend.stream",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend.stream",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"ctx":"llm.Context[str]","genre":"str"}',
                "mirascope.trace.arg_values": '{"ctx":{"deps":"As a librarian,"},"genre":"adventure"}',
                "mirascope.response.provider_id": "openai",
                "mirascope.response.model_id": "openai/gpt-4o-mini",
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"As a librarian, Recommend a adventure book."}],"name":null}]',
                "mirascope.response.content": "[]",
                "mirascope.trace.output": "",
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_traced_async_call(span_exporter: InMemorySpanExporter) -> None:
    """Test @ops.trace on async @llm.call creates TracedAsyncCall and returns AsyncResponse directly."""

    @ops.trace
    @llm.call("openai/gpt-4o-mini")
    async def recommend(genre: str) -> str:
        return f"Recommend a {genre} book."

    assert isinstance(recommend, ops.TracedAsyncCall)

    response = await recommend("horror")
    assert response.content

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend.call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend.call",
                "mirascope.fn.module": "ops._internal.test_tracing",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"genre":"str"}',
                "mirascope.trace.arg_values": '{"genre":"horror"}',
                "mirascope.response.provider_id": "openai",
                "mirascope.response.model_id": "openai/gpt-4o-mini",
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"Recommend a horror book."}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"I recommend **\\"The Haunting of Hill House\\" by Shirley Jackson**. It\'s a classic gothic horror novel that explores themes of fear, isolation, and the supernatural. The story follows a group of people who stay at an old mansion to study its paranormal activities. Jackson\'s writing masterfully builds tension and unease, making it a must-read for horror enthusiasts."}]',
                "mirascope.response.usage": '{"input_tokens":12,"output_tokens":74,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":86}',
                "mirascope.trace.output": "I recommend **\"The Haunting of Hill House\" by Shirley Jackson**. It's a classic gothic horror novel that explores themes of fear, isolation, and the supernatural. The story follows a group of people who stay at an old mansion to study its paranormal activities. Jackson's writing masterfully builds tension and unease, making it a must-read for horror enthusiasts.",
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
def test_traced_call_with_tags(span_exporter: InMemorySpanExporter) -> None:
    """Test @ops.trace(tags=[...]) passes tags to TracedCall."""

    @ops.trace(tags=["production", "recommendations"])
    @llm.call("openai/gpt-4o-mini")
    def recommend(genre: str) -> str:
        return f"Recommend a {genre} book."

    response = recommend("romance")
    assert response.content

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend.call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend.call",
                "mirascope.fn.module": "ops._internal.test_tracing",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"genre":"str"}',
                "mirascope.trace.arg_values": '{"genre":"romance"}',
                "mirascope.trace.tags": ("production", "recommendations"),
                "mirascope.response.provider_id": "openai",
                "mirascope.response.model_id": "openai/gpt-4o-mini",
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"Recommend a romance book."}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"One great romance book to consider is **\\"The Hating Game\\" by Sally Thorne**. It features a fun and engaging enemies-to-lovers storyline set in a corporate office, filled with witty banter and undeniable chemistry. The dynamic between the two main characters, Lucy and Joshua, is both humorous and heartfelt, making for a captivating read. If you enjoy sharp dialogue and a slow-burn romance, this book is definitely worth picking up!"}]',
                "mirascope.response.usage": '{"input_tokens":12,"output_tokens":91,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":103}',
                "mirascope.trace.output": 'One great romance book to consider is **"The Hating Game" by Sally Thorne**. It features a fun and engaging enemies-to-lovers storyline set in a corporate office, filled with witty banter and undeniable chemistry. The dynamic between the two main characters, Lucy and Joshua, is both humorous and heartfelt, making for a captivating read. If you enjoy sharp dialogue and a slow-burn romance, this book is definitely worth picking up!',
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
def test_traced_context_call(span_exporter: InMemorySpanExporter) -> None:
    """Test @ops.trace on @llm.call with context creates TracedContextCall and returns ContextResponse directly."""

    @ops.trace
    @llm.call("openai/gpt-4o-mini")
    def recommend(ctx: llm.Context[str], genre: str) -> str:
        return f"{ctx.deps} Recommend a {genre} book."

    assert isinstance(recommend, ops.TracedContextCall)

    ctx = llm.Context(deps="As a librarian,")
    response = recommend(ctx, "fantasy")
    assert response.content

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend.call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend.call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"ctx":"llm.Context[str]","genre":"str"}',
                "mirascope.trace.arg_values": '{"ctx":{"deps":"As a librarian,"},"genre":"fantasy"}',
                "mirascope.response.provider_id": "openai",
                "mirascope.response.model_id": "openai/gpt-4o-mini",
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"As a librarian, Recommend a fantasy book."}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"I recommend **\\"The Name of the Wind\\" by Patrick Rothfuss**. It\'s the first book in the *Kingkiller Chronicle* series and follows the journey of Kvothe, a gifted young man who becomes a legendary figure. The story beautifully weaves together magic, music, and adventure, all told with lyrical prose. It\'s a captivating read for anyone who loves deep world-building and intricate storytelling!"}]',
                "mirascope.response.usage": '{"input_tokens":16,"output_tokens":82,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":98}',
                "mirascope.trace.output": "I recommend **\"The Name of the Wind\" by Patrick Rothfuss**. It's the first book in the *Kingkiller Chronicle* series and follows the journey of Kvothe, a gifted young man who becomes a legendary figure. The story beautifully weaves together magic, music, and adventure, all told with lyrical prose. It's a captivating read for anyone who loves deep world-building and intricate storytelling!",
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_traced_async_context_call(span_exporter: InMemorySpanExporter) -> None:
    """Test @ops.trace on async @llm.call with context creates TracedAsyncContextCall and returns AsyncContextResponse directly."""

    @ops.trace
    @llm.call("openai/gpt-4o-mini")
    async def recommend(ctx: llm.Context[str], genre: str) -> str:
        return f"{ctx.deps} Recommend a {genre} book."

    assert isinstance(recommend, ops.TracedAsyncContextCall)

    ctx = llm.Context(deps="As a librarian,")
    response = await recommend(ctx, "mystery")
    assert response.content

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend.call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend.call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"ctx":"llm.Context[str]","genre":"str"}',
                "mirascope.trace.arg_values": '{"ctx":{"deps":"As a librarian,"},"genre":"mystery"}',
                "mirascope.response.provider_id": "openai",
                "mirascope.response.model_id": "openai/gpt-4o-mini",
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"As a librarian, Recommend a mystery book."}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"I recommend *The No. 1 Ladies\' Detective Agency* by Alexander McCall Smith. This charming mystery features Precious Ramotswe, Botswana\'s first female detective, who uses her intuition and keen observation skills to solve cases in her community. The book is both engaging and uplifting, offering a unique blend of mystery, humor, and cultural insight. It\'s the first in a beloved series, making it a great starting point for readers who enjoy cozy mysteries."}]',
                "mirascope.response.usage": '{"input_tokens":16,"output_tokens":92,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":108}',
                "mirascope.trace.output": "I recommend *The No. 1 Ladies' Detective Agency* by Alexander McCall Smith. This charming mystery features Precious Ramotswe, Botswana's first female detective, who uses her intuition and keen observation skills to solve cases in her community. The book is both engaging and uplifting, offering a unique blend of mystery, humor, and cultural insight. It's the first in a beloved series, making it a great starting point for readers who enjoy cozy mysteries.",
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
def test_traced_context_call_wrapped_call_method(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test TracedContextCall.wrapped.call() returns ContextResponse directly."""

    @ops.trace
    @llm.call("openai/gpt-4o-mini")
    def recommend(ctx: llm.Context[str], genre: str) -> str:
        return f"{ctx.deps} Recommend a {genre} book."

    ctx = llm.Context(deps="As a librarian,")
    response = recommend.call(ctx, "historical")
    assert response.content
    assert hasattr(response, "content")
    assert not hasattr(response, "span_id")

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend.call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend.call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"ctx":"llm.Context[str]","genre":"str"}',
                "mirascope.trace.arg_values": '{"ctx":{"deps":"As a librarian,"},"genre":"historical"}',
                "mirascope.response.provider_id": "openai",
                "mirascope.response.model_id": "openai/gpt-4o-mini",
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"As a librarian, Recommend a historical book."}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"I recommend **\\"The Warmth of Other Suns: The Epic Story of America\'s Great Migration\\" by Isabel Wilkerson**. This compelling historical narrative chronicles the journey of African Americans who moved from the rural South to urban centers in the North and West between 1915 and 1970. Through the stories of three individuals, Wilkerson explores the profound social, cultural, and political changes brought about by this migration, making it not only an essential read but an engaging and personal look at a pivotal moment in American history."}]',
                "mirascope.response.usage": '{"input_tokens":16,"output_tokens":107,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":123}',
                "mirascope.trace.output": 'I recommend **"The Warmth of Other Suns: The Epic Story of America\'s Great Migration" by Isabel Wilkerson**. This compelling historical narrative chronicles the journey of African Americans who moved from the rural South to urban centers in the North and West between 1915 and 1970. Through the stories of three individuals, Wilkerson explores the profound social, cultural, and political changes brought about by this migration, making it not only an essential read but an engaging and personal look at a pivotal moment in American history.',
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_traced_async_context_call_wrapped_call_method(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test TracedAsyncContextCall.wrapped.call() returns AsyncContextResponse directly."""

    @ops.trace
    @llm.call("openai/gpt-4o-mini")
    async def recommend(ctx: llm.Context[str], genre: str) -> str:
        return f"{ctx.deps} Recommend a {genre} book."

    ctx = llm.Context(deps="As a librarian,")
    response = await recommend.call(ctx, "thriller")
    assert response.content
    assert hasattr(response, "content")
    assert not hasattr(response, "span_id")

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend.call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend.call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"ctx":"llm.Context[str]","genre":"str"}',
                "mirascope.trace.arg_values": '{"ctx":{"deps":"As a librarian,"},"genre":"thriller"}',
                "mirascope.response.provider_id": "openai",
                "mirascope.response.model_id": "openai/gpt-4o-mini",
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"As a librarian, Recommend a thriller book."}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"I recommend **\\"The Girl on the Train\\" by Paula Hawkins**. This psychological thriller weaves together the lives of three women, exploring themes of obsession, memory, and deception. With its gripping plot and unexpected twists, the story keeps readers on the edge of their seats. The intricately crafted characters and their intertwined narratives make it a captivating read. Perfect for fans of suspenseful, character-driven stories!"}]',
                "mirascope.response.usage": '{"input_tokens":16,"output_tokens":83,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":99}',
                "mirascope.trace.output": 'I recommend **"The Girl on the Train" by Paula Hawkins**. This psychological thriller weaves together the lives of three women, exploring themes of obsession, memory, and deception. With its gripping plot and unexpected twists, the story keeps readers on the edge of their seats. The intricately crafted characters and their intertwined narratives make it a captivating read. Perfect for fans of suspenseful, character-driven stories!',
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
def test_traced_context_call_with_tags(span_exporter: InMemorySpanExporter) -> None:
    """Test @ops.trace(tags=[...]) on @llm.call with context creates TracedContextCall with tags."""

    @ops.trace(tags=["context-tag"])
    @llm.call("openai/gpt-4o-mini")
    def recommend(ctx: llm.Context[str], genre: str) -> str:
        return f"{ctx.deps} Recommend a {genre} book."

    assert isinstance(recommend, ops.TracedContextCall)

    ctx = llm.Context(deps="As a librarian,")
    response = recommend(ctx, "science fiction")
    assert response.content

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend.call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend.call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"ctx":"llm.Context[str]","genre":"str"}',
                "mirascope.trace.arg_values": '{"ctx":{"deps":"As a librarian,"},"genre":"science fiction"}',
                "mirascope.trace.tags": ("context-tag",),
                "mirascope.response.provider_id": "openai",
                "mirascope.response.model_id": "openai/gpt-4o-mini",
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"As a librarian, Recommend a science fiction book."}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"I recommend **\\"The Dispossessed\\" by Ursula K. Le Guin**. This thought-provoking novel explores themes of anarchism, capitalism, and the nature of society through the lens of two contrasting worlds: one that values individualism and wealth and another that promotes communal living and equality. Le Guin\'s well-crafted characters and intricate world-building create a rich narrative that challenges readers to reflect on their own societal structures. It\'s a classic that continues to resonate today."}]',
                "mirascope.response.usage": '{"input_tokens":17,"output_tokens":93,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":110}',
                "mirascope.trace.output": "I recommend **\"The Dispossessed\" by Ursula K. Le Guin**. This thought-provoking novel explores themes of anarchism, capitalism, and the nature of society through the lens of two contrasting worlds: one that values individualism and wealth and another that promotes communal living and equality. Le Guin's well-crafted characters and intricate world-building create a rich narrative that challenges readers to reflect on their own societal structures. It's a classic that continues to resonate today.",
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_traced_async_context_call_with_tags(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test @ops.trace(tags=[...]) on async @llm.call with context creates TracedAsyncContextCall with tags."""

    @ops.trace(tags=["async-context-tag"])
    @llm.call("openai/gpt-4o-mini")
    async def recommend(ctx: llm.Context[str], genre: str) -> str:
        return f"{ctx.deps} Recommend a {genre} book."

    assert isinstance(recommend, ops.TracedAsyncContextCall)

    ctx = llm.Context(deps="As a librarian,")
    response = await recommend(ctx, "dystopian")
    assert response.content

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend.call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend.call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"ctx":"llm.Context[str]","genre":"str"}',
                "mirascope.trace.arg_values": '{"ctx":{"deps":"As a librarian,"},"genre":"dystopian"}',
                "mirascope.trace.tags": ("async-context-tag",),
                "mirascope.response.provider_id": "openai",
                "mirascope.response.model_id": "openai/gpt-4o-mini",
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"As a librarian, Recommend a dystopian book."}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"I recommend **\\"The Handmaid\'s Tale\\" by Margaret Atwood**. Set in a totalitarian society where women are stripped of their rights, the novel explores themes of gender, power, and individuality. Atwood\'s rich prose and compelling characters make it a thought-provoking read that remains relevant today. It also raises important questions about autonomy and society\'s role in personal freedoms. Perfect for anyone interested in dystopian fiction!"}]',
                "mirascope.response.usage": '{"input_tokens":17,"output_tokens":86,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":103}',
                "mirascope.trace.output": "I recommend **\"The Handmaid's Tale\" by Margaret Atwood**. Set in a totalitarian society where women are stripped of their rights, the novel explores themes of gender, power, and individuality. Atwood's rich prose and compelling characters make it a thought-provoking read that remains relevant today. It also raises important questions about autonomy and society's role in personal freedoms. Perfect for anyone interested in dystopian fiction!",
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
def test_traced_context_call_with_metadata(span_exporter: InMemorySpanExporter) -> None:
    """Test @ops.trace(metadata={...}) on @llm.call with context exports metadata."""

    @ops.trace(metadata={"env": "test", "version": "1.0"})
    @llm.call("openai/gpt-4o-mini")
    def recommend(ctx: llm.Context[str], genre: str) -> str:
        return f"{ctx.deps} Recommend a {genre} book."

    assert isinstance(recommend, ops.TracedContextCall)

    ctx = llm.Context(deps="As a librarian,")
    response = recommend(ctx, "mystery")
    assert response.content

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data["attributes"]["mirascope.trace.metadata"] == snapshot(
        '{"env":"test","version":"1.0"}'
    )


def test_sync_trace_annotate(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test Trace.annotate sends annotation to API."""
    mock_client = MagicMock()

    with patch(
        "mirascope.ops._internal.traced_functions.get_sync_client",
        return_value=mock_client,
    ):

        @ops.trace
        def process(x: int) -> int:
            return x * 2

        trace = process.wrapped(5)
        trace.annotate(
            label="pass", reasoning="correct output", metadata={"score": 100}
        )

        mock_client.annotations.create.assert_called_once_with(
            otel_span_id=trace.span_id,
            otel_trace_id=trace.trace_id,
            label="pass",
            reasoning="correct output",
            metadata={"score": 100},
        )


@pytest.mark.asyncio
async def test_async_trace_annotate(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test AsyncTrace.annotate sends annotation to API."""
    mock_client = MagicMock()
    mock_client.annotations.create = AsyncMock()

    with patch(
        "mirascope.ops._internal.traced_functions.get_async_client",
        return_value=mock_client,
    ):

        @ops.trace
        async def process(x: int) -> int:
            return x * 2

        trace = await process.wrapped(5)
        await trace.annotate(
            label="fail", reasoning="wrong output", metadata={"expected": 10}
        )

        mock_client.annotations.create.assert_called_once_with(
            otel_span_id=trace.span_id,
            otel_trace_id=trace.trace_id,
            label="fail",
            reasoning="wrong output",
            metadata={"expected": 10},
        )


def test_sync_trace_annotate_noop_span() -> None:
    """Test Trace.annotate does nothing for no-op spans."""
    with patch(
        "mirascope.ops._internal.traced_functions.get_sync_client",
    ) as mock_get_client:
        from mirascope.ops._internal.spans import Span
        from mirascope.ops._internal.traced_functions import Trace

        noop_span = Span("test")
        trace = Trace(result=42, span=noop_span)
        trace.annotate(label="pass")

        mock_get_client.assert_not_called()


@pytest.mark.asyncio
async def test_async_trace_annotate_noop_span() -> None:
    """Test AsyncTrace.annotate does nothing for no-op spans."""
    with patch(
        "mirascope.ops._internal.traced_functions.get_async_client",
    ) as mock_get_client:
        from mirascope.ops._internal.spans import Span
        from mirascope.ops._internal.traced_functions import AsyncTrace

        noop_span = Span("test")
        trace = AsyncTrace(result=42, span=noop_span)
        await trace.annotate(label="pass")

        mock_get_client.assert_not_called()


def test_sync_trace_with_span_injection(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test @trace decorator injects Span as first parameter when requested."""

    @ops.trace
    def process(trace_ctx: ops.Span, value: int) -> int:
        trace_ctx.info(f"Processing value: {value}")
        return value * 2

    # Call WITHOUT trace_ctx - it should be injected
    result = process(5)
    assert result == 10

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data == snapshot(
        {
            "name": "process",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "process",
                "mirascope.fn.module": "ops._internal.test_tracing",
                "mirascope.fn.is_async": False,
                # Note: trace_ctx is NOT in arg_types or arg_values
                "mirascope.trace.arg_types": '{"value":"int"}',
                "mirascope.trace.arg_values": '{"value":5}',
                "mirascope.trace.output": 10,
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [
                {
                    "name": "info",
                    "attributes": {"level": "info", "message": "Processing value: 5"},
                }
            ],
        }
    )


def test_sync_trace_with_span_injection_wrapped(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test @trace decorator with span injection returns Trace from wrapped()."""

    @ops.trace
    def process(trace_ctx: ops.Span, value: int) -> int:
        trace_ctx.debug("Debug message")
        return value * 3

    wrapped_result = process.wrapped(7)

    assert wrapped_result.result == 21
    assert wrapped_result.span_id is not None
    assert wrapped_result.trace_id is not None

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data["attributes"]["mirascope.trace.arg_types"] == '{"value":"int"}'
    assert span_data["attributes"]["mirascope.trace.arg_values"] == '{"value":7}'
    assert span_data["events"][0]["name"] == "debug"


@pytest.mark.asyncio
async def test_async_trace_with_span_injection(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test @trace decorator injects Span for async functions."""

    @ops.trace
    async def process(trace_ctx: ops.Span, value: int) -> int:
        trace_ctx.warning(f"Processing async: {value}")
        return value * 4

    # Call WITHOUT trace_ctx - it should be injected
    result = await process(3)
    assert result == 12

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data == snapshot(
        {
            "name": "process",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "process",
                "mirascope.fn.module": "ops._internal.test_tracing",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"value":"int"}',
                "mirascope.trace.arg_values": '{"value":3}',
                "mirascope.trace.output": 12,
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [
                {
                    "name": "warning",
                    "attributes": {
                        "level": "warning",
                        "message": "Processing async: 3",
                    },
                }
            ],
        }
    )


@pytest.mark.asyncio
async def test_async_trace_with_span_injection_wrapped(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test @trace decorator with span injection returns AsyncTrace from wrapped()."""

    @ops.trace
    async def process(trace_ctx: ops.Span, value: int) -> int:
        trace_ctx.error("Error occurred")
        return value * 5

    wrapped_result = await process.wrapped(2)

    assert wrapped_result.result == 10
    assert wrapped_result.span_id is not None
    assert wrapped_result.trace_id is not None

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data["attributes"]["mirascope.trace.arg_types"] == '{"value":"int"}'
    assert span_data["events"][0]["name"] == "error"


def test_sync_trace_with_span_injection_and_tags(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test @trace with span injection supports tags and metadata."""

    @ops.trace(tags=["span-test"], metadata={"env": "test"})
    def process(trace_ctx: ops.Span, value: str) -> str:
        trace_ctx.critical("Critical message")
        return value.upper()

    result = process("hello")
    assert result == "HELLO"

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data["attributes"]["mirascope.trace.tags"] == ("span-test",)
    assert span_data["attributes"]["mirascope.trace.metadata"] == '{"env":"test"}'
    assert span_data["events"][0]["name"] == "critical"


@pytest.mark.asyncio
async def test_async_trace_with_span_injection_and_tags(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test @trace with span injection supports tags and metadata for async functions."""

    @ops.trace(tags=["async-span-test"], metadata={"async": "true"})
    async def process(trace_ctx: ops.Span, value: str) -> str:
        trace_ctx.info("Async processing")
        return value.lower()

    result = await process("HELLO")
    assert result == "hello"

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data["attributes"]["mirascope.trace.tags"] == ("async-span-test",)
    assert span_data["attributes"]["mirascope.trace.metadata"] == '{"async":"true"}'
    assert span_data["events"][0]["name"] == "info"


def test_trace_returns_correct_type_for_span_function() -> None:
    """Test that @trace returns TracedSpanFunction for functions with trace_ctx."""

    @ops.trace
    def with_span(trace_ctx: ops.Span, x: int) -> int:
        return x

    @ops.trace
    async def async_with_span(trace_ctx: ops.Span, x: int) -> int:
        return x

    @ops.trace
    def without_span(x: int) -> int:
        return x

    assert isinstance(with_span, ops.TracedSpanFunction)
    assert isinstance(async_with_span, ops.AsyncTracedSpanFunction)
    assert isinstance(without_span, ops.TracedFunction)


def test_fn_wants_span_detection() -> None:
    """Test fn_wants_span correctly detects functions wanting span injection."""
    from mirascope.ops._internal.protocols import fn_wants_span
    from mirascope.ops._internal.spans import Span

    def with_span(trace_ctx: ops.Span, x: int) -> int:
        return x

    def wrong_name(span: ops.Span, x: int) -> int:
        return x

    def no_annotation(trace_ctx, x: int) -> int:  # pyright: ignore[reportMissingParameterType]  # noqa: ANN001
        return x

    def wrong_type(trace_ctx: str, x: int) -> int:
        return x

    def no_params() -> None:
        pass

    assert fn_wants_span(with_span) is True
    assert fn_wants_span(wrong_name) is False
    assert fn_wants_span(no_annotation) is False
    assert fn_wants_span(wrong_type) is False
    assert fn_wants_span(no_params) is False

    # Test with direct Span annotation (not string)
    def with_direct_span(trace_ctx: Span, x: int) -> int:
        return x

    # Clear the __annotations__ to force evaluation
    with_direct_span.__annotations__ = {"trace_ctx": Span, "x": int, "return": int}
    assert fn_wants_span(with_direct_span) is True

    # Test with a callable that raises on signature inspection
    # Use a mock to reliably trigger the exception path across all Python versions
    # (In Python 3.11+, many built-ins like `print` now have valid signatures)
    def some_func() -> None:
        pass

    with patch("inspect.signature", side_effect=ValueError("no signature")):
        assert fn_wants_span(some_func) is False

    # Test with annotation that's neither string nor type (edge case)
    def with_weird_annotation(trace_ctx: int, x: int) -> int:
        return x

    # Replace annotation with something unusual
    with_weird_annotation.__annotations__["trace_ctx"] = 123
    assert fn_wants_span(with_weird_annotation) is False

    # Test with a fake Span class that has the right name and module
    # This tests the fallback path when `annotation is Span` is False
    class FakeSpan:
        pass

    FakeSpan.__name__ = "Span"
    FakeSpan.__module__ = "mirascope.ops._internal.spans"

    def with_fake_span(trace_ctx: int, x: int) -> int:
        return x

    with_fake_span.__annotations__["trace_ctx"] = FakeSpan
    assert fn_wants_span(with_fake_span) is True

    # Test with a class that has wrong module
    class WrongModuleSpan:
        pass

    WrongModuleSpan.__name__ = "Span"
    WrongModuleSpan.__module__ = "wrong.module"

    def with_wrong_module(trace_ctx: int, x: int) -> int:
        return x

    with_wrong_module.__annotations__["trace_ctx"] = WrongModuleSpan
    assert fn_wants_span(with_wrong_module) is False


def test_sync_trace_with_span_multiple_args(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test span injection with multiple arguments."""

    @ops.trace
    def process(trace_ctx: ops.Span, a: int, b: str, c: float = 1.5) -> str:
        trace_ctx.info(f"a={a}, b={b}, c={c}")
        return f"{a}-{b}-{c}"

    result = process(10, "test")
    assert result == "10-test-1.5"

    spans = span_exporter.get_finished_spans()
    span_data = extract_span_data(spans[0])

    # Verify trace_ctx is NOT in the arguments
    assert span_data["attributes"]["mirascope.trace.arg_types"] == snapshot(
        '{"a":"int","b":"str","c":"float"}'
    )
    assert span_data["attributes"]["mirascope.trace.arg_values"] == snapshot(
        '{"a":10,"b":"test","c":1.5}'
    )
