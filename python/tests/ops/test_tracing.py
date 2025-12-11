"""Tests for `mirascope.ops.tracing`."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any, TypeVar

import pytest
from inline_snapshot import snapshot
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from mirascope import llm, ops
from mirascope.ops._internal.exporters.utils import format_span_id, format_trace_id

from .utils import extract_span_data

T = TypeVar("T")


@pytest.fixture(autouse=True, scope="function")
def initialize() -> Generator[None, None, None]:
    """Initialize ops configuration and LLM instrumentation for each test."""
    ops.configure()
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
            "name": "call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"args":"P.args","kwargs":"P.kwargs"}',
                "mirascope.trace.arg_values": '{"args":["fantasy"],"kwargs":{}}',
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
            "name": "call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"args":"P.args","kwargs":"P.kwargs"}',
                "mirascope.trace.arg_values": '{"args":["mystery"],"kwargs":{}}',
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
            "name": "call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"args":"P.args","kwargs":"P.kwargs"}',
                "mirascope.trace.arg_values": '{"args":["scifi"],"kwargs":{}}',
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
            "name": "stream",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "stream",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"args":"P.args","kwargs":"P.kwargs"}',
                "mirascope.trace.arg_values": '{"args":["adventure"],"kwargs":{}}',
                "mirascope.trace.output": "**[No Content]**",
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
            "name": "call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"args":"P.args","kwargs":"P.kwargs"}',
                "mirascope.trace.arg_values": '{"args":["fantasy"],"kwargs":{}}',
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
            "name": "stream",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "stream",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"args":"P.args","kwargs":"P.kwargs"}',
                "mirascope.trace.arg_values": '{"args":["adventure"],"kwargs":{}}',
                "mirascope.trace.output": "**[No Content]**",
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
            "name": "call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"args":"P.args","kwargs":"P.kwargs"}',
                "mirascope.trace.arg_values": '{"args":["horror"],"kwargs":{}}',
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
            "name": "call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"args":"P.args","kwargs":"P.kwargs"}',
                "mirascope.trace.arg_values": '{"args":["horror"],"kwargs":{}}',
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
            "name": "stream",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "stream",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"args":"P.args","kwargs":"P.kwargs"}',
                "mirascope.trace.arg_values": '{"args":["adventure"],"kwargs":{}}',
                "mirascope.trace.output": "**[No Content]**",
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
            "name": "call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"ctx":"Context","args":"P.args","kwargs":"P.kwargs"}',
                "mirascope.trace.arg_values": '{"ctx":{"deps":"As a librarian,"},"args":["fantasy"],"kwargs":{}}',
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
            "name": "stream",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "stream",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"ctx":"Context","args":"P.args","kwargs":"P.kwargs"}',
                "mirascope.trace.arg_values": '{"ctx":{"deps":"As a librarian,"},"args":["adventure"],"kwargs":{}}',
                "mirascope.trace.output": "**[No Content]**",
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
            "name": "call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"ctx":"Context","args":"P.args","kwargs":"P.kwargs"}',
                "mirascope.trace.arg_values": '{"ctx":{"deps":"As a librarian,"},"args":["mystery"],"kwargs":{}}',
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
            "name": "stream",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "stream",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"ctx":"Context","args":"P.args","kwargs":"P.kwargs"}',
                "mirascope.trace.arg_values": '{"ctx":{"deps":"As a librarian,"},"args":["adventure"],"kwargs":{}}',
                "mirascope.trace.output": "**[No Content]**",
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
            "name": "call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"args":"P.args","kwargs":"P.kwargs"}',
                "mirascope.trace.arg_values": '{"args":["horror"],"kwargs":{}}',
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
            "name": "call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"args":"P.args","kwargs":"P.kwargs"}',
                "mirascope.trace.arg_values": '{"args":["romance"],"kwargs":{}}',
                "mirascope.trace.tags": ("production", "recommendations"),
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
            "name": "call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"ctx":"Context","args":"P.args","kwargs":"P.kwargs"}',
                "mirascope.trace.arg_values": '{"ctx":{"deps":"As a librarian,"},"args":["fantasy"],"kwargs":{}}',
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
            "name": "call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"ctx":"Context","args":"P.args","kwargs":"P.kwargs"}',
                "mirascope.trace.arg_values": '{"ctx":{"deps":"As a librarian,"},"args":["mystery"],"kwargs":{}}',
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
            "name": "call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"ctx":"Context","args":"P.args","kwargs":"P.kwargs"}',
                "mirascope.trace.arg_values": '{"ctx":{"deps":"As a librarian,"},"args":["historical"],"kwargs":{}}',
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
            "name": "call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"ctx":"Context","args":"P.args","kwargs":"P.kwargs"}',
                "mirascope.trace.arg_values": '{"ctx":{"deps":"As a librarian,"},"args":["thriller"],"kwargs":{}}',
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
            "name": "call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"ctx":"Context","args":"P.args","kwargs":"P.kwargs"}',
                "mirascope.trace.arg_values": '{"ctx":{"deps":"As a librarian,"},"args":["science fiction"],"kwargs":{}}',
                "mirascope.trace.tags": ("context-tag",),
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
            "name": "call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"ctx":"Context","args":"P.args","kwargs":"P.kwargs"}',
                "mirascope.trace.arg_values": '{"ctx":{"deps":"As a librarian,"},"args":["dystopian"],"kwargs":{}}',
                "mirascope.trace.tags": ("async-context-tag",),
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
