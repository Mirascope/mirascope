"""OpenTelemetry integration tests for `llm.Model.stream_async`."""

from __future__ import annotations

from collections.abc import AsyncIterator, Generator
from unittest.mock import AsyncMock, Mock

import httpx
import openai
import pytest
from inline_snapshot import snapshot
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from mirascope import llm, ops
from mirascope.ops._internal.configuration import set_tracer
from tests.ops.utils import span_snapshot


@pytest.fixture(autouse=True, scope="function")
def initialize(tracer_provider: TracerProvider) -> Generator[None, None, None]:
    """Initialize ops configuration and LLM instrumentation for each test."""
    ops.configure(tracer_provider=tracer_provider)
    ops.instrument_llm()
    yield
    ops.uninstrument_llm()


def _math_messages() -> list[llm.Message]:
    """Return a simple math prompt for streaming tests."""
    return [llm.messages.user("What is 4200 + 42?")]


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_model_stream_async_exports_genai_span(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that async streaming a model call exports the correct OpenTelemetry span."""
    model = llm.Model(model_id="openai/gpt-4o-mini")

    response = await model.stream_async(_math_messages())
    await response.finish()

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span_dict = span_snapshot(spans[0])
    assert span_dict == snapshot(
        {
            "name": "chat openai/gpt-4o-mini",
            "kind": "CLIENT",
            "status": "UNSET",
            "attributes": {
                "gen_ai.operation.name": "chat",
                "gen_ai.provider.name": "openai",
                "gen_ai.request.model": "openai/gpt-4o-mini",
                "gen_ai.output.type": "text",
                "gen_ai.response.model": "openai/gpt-4o-mini",
                "gen_ai.response.finish_reasons": ["stop"],
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"What is 4200 + 42?"}]}]',
                "gen_ai.output.messages": '[{"role":"assistant","parts":[{"type":"text","content":"4200 + 42 equals 4242."}],"finish_reason":"stop"}]',
                "gen_ai.usage.input_tokens": 16,
                "gen_ai.usage.output_tokens": 11,
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"What is 4200 + 42?"}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"4200 + 42 equals 4242."}]',
                "mirascope.response.usage": '{"input_tokens":16,"output_tokens":11,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":27}',
            },
        }
    )


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_model_stream_async_without_instrumentation(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that async streaming without instrumentation creates no spans."""
    ops.uninstrument_llm()

    model = llm.Model(model_id="openai/gpt-4o-mini")
    response = await model.stream_async(_math_messages())
    await response.finish()

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 0


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_model_stream_async_with_tracer_set_to_none(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that async streaming with tracer set to None creates no spans."""
    set_tracer(None)

    model = llm.Model(model_id="openai/gpt-4o-mini")
    response = await model.stream_async(_math_messages())
    await response.finish()

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 0


@pytest.mark.asyncio
async def test_model_stream_async_with_error(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that async streaming errors are recorded in the span."""
    # Create a mock provider that raises an error
    mock_provider = Mock()
    mock_provider.id = "openai"
    mock_provider.error_map = {}
    mock_provider.stream_async = AsyncMock(
        side_effect=openai.APIError(
            "Server error occurred",
            request=httpx.Request("POST", "https://example.com"),
            body=None,
        )
    )

    llm.register_provider(mock_provider, scope="openai/")

    model = llm.Model(model_id="openai/gpt-4o-mini")
    with pytest.raises(openai.APIError):
        await model.stream_async(_math_messages())

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span_dict = span_snapshot(spans[0])
    assert span_dict == snapshot(
        {
            "name": "chat openai/gpt-4o-mini",
            "kind": "CLIENT",
            "status": "ERROR",
            "attributes": {
                "gen_ai.operation.name": "chat",
                "gen_ai.provider.name": "openai",
                "gen_ai.request.model": "openai/gpt-4o-mini",
                "gen_ai.output.type": "text",
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"What is 4200 + 42?"}]}]',
                "error.type": "APIError",
                "error.message": "Server error occurred",
            },
        }
    )


@pytest.mark.asyncio
async def test_model_stream_async_iterator_error_records_exception(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that async streaming iterator errors are recorded in the span."""

    async def _chunk_iterator() -> AsyncIterator[llm.StreamResponseChunk]:
        """Return an async chunk iterator that raises to simulate stream failure."""
        yield llm.TextStartChunk()
        yield llm.TextChunk(delta="partial")
        raise RuntimeError("async chunk boom")

    # Create a mock provider that returns a failing async stream
    mock_provider = Mock()
    mock_provider.id = "openai"
    mock_provider.error_map = {}
    mock_provider.stream_async = AsyncMock(
        return_value=llm.AsyncStreamResponse(
            provider_id="openai",
            model_id="openai/gpt-4o-mini",
            provider_model_name="gpt-4o-mini:responses",
            params={},
            tools=None,
            format=None,
            input_messages=_math_messages(),
            chunk_iterator=_chunk_iterator(),
        )
    )

    llm.register_provider(mock_provider, scope="openai/")

    model = llm.Model(model_id="openai/gpt-4o-mini")
    response = await model.stream_async(_math_messages())
    with pytest.raises(RuntimeError):
        await response.finish()

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]
    assert span.status.status_code.name == "ERROR"
    attrs = span.attributes or {}
    assert attrs["error.type"] == "RuntimeError"
    assert attrs["error.message"] == "async chunk boom"
