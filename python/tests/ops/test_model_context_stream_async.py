"""OpenTelemetry integration tests for `llm.Model.context_stream_async`."""

from __future__ import annotations

from collections.abc import AsyncIterator, Generator, Sequence
from typing import Any

import pytest
from inline_snapshot import snapshot
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

from mirascope import llm, ops
from mirascope.llm.messages import Message
from mirascope.llm.responses import AsyncContextStreamResponse, StreamResponseChunk
from mirascope.ops._internal.configuration import set_tracer
from mirascope.ops._internal.instrumentation.llm import llm as instrument_module
from tests.ops.utils import span_snapshot


@pytest.fixture(autouse=True, scope="function")
def initialize() -> Generator[None, None, None]:
    """Initialize ops configuration and LLM instrumentation for each test."""
    ops.configure()
    ops.instrument_llm()
    yield
    ops.uninstrument_llm()


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_model_context_stream_async_exports_genai_span(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that streaming a model call exports the correct OpenTelemetry span."""
    model = llm.Model(model_id="openai/gpt-4o-mini")
    ctx = llm.Context(deps={"tenant": "kai"})
    messages: list[Message] = [
        llm.messages.system("You are a concise assistant."),
        llm.messages.user("Say hello to the user named Kai."),
    ]

    response = await model.context_stream_async(ctx=ctx, messages=messages)
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
                "gen_ai.system_instructions": '[{"type":"text","content":"You are a concise assistant."}]',
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"Say hello to the user named Kai."}]}]',
                "gen_ai.output.messages": '[{"role":"assistant","parts":[{"type":"text","content":"Hello, Kai!"}],"finish_reason":"stop"}]',
            },
        }
    )


@pytest.mark.asyncio
async def test_model_context_stream_async_without_tracer_returns_response(
    span_exporter: InMemorySpanExporter, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that streaming a model call returns the response object."""
    set_tracer(None)
    dummy_response = object()

    async def _fake_context_stream_async(
        self: llm.Model,
        *,
        ctx: llm.Context[Any],
        messages: Sequence[llm.Message],
        tools: object | None = None,
        format: object | None = None,
    ) -> object:
        return dummy_response

    monkeypatch.setattr(
        instrument_module,
        "_ORIGINAL_MODEL_CONTEXT_STREAM_ASYNC",
        _fake_context_stream_async,
    )

    model = llm.Model(model_id="openai/gpt-4o-mini")
    ctx = llm.Context(deps={})
    messages: list[Message] = [llm.messages.user("hi")]

    response = await model.context_stream_async(ctx=ctx, messages=messages)

    assert response is dummy_response
    assert span_exporter.get_finished_spans() == ()


@pytest.mark.asyncio
async def test_model_context_stream_async_records_error_on_exception(
    span_exporter: InMemorySpanExporter, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that streaming a model call exports the correct OpenTelemetry span."""

    async def _failing_context_stream_async(
        self: llm.Model,
        *,
        ctx: llm.Context[Any],
        messages: Sequence[llm.Message],
        tools: object | None = None,
        format: object | None = None,
    ) -> object:
        raise ValueError("error")

    monkeypatch.setattr(
        instrument_module,
        "_ORIGINAL_MODEL_CONTEXT_STREAM_ASYNC",
        _failing_context_stream_async,
    )

    model = llm.Model(model_id="openai/gpt-4o-mini")
    ctx = llm.Context(deps={})
    messages: list[Message] = [llm.messages.user("hi")]

    with pytest.raises(ValueError, match="error"):
        await model.context_stream_async(ctx=ctx, messages=messages)

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
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"hi"}]}]',
                "error.type": "ValueError",
                "error.message": "error",
            },
        }
    )


@pytest.mark.asyncio
async def test_model_context_stream_async_records_error_on_chunk_failure(
    span_exporter: InMemorySpanExporter, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that streaming a model call exports the correct OpenTelemetry span."""

    async def _chunk_error_iterator() -> AsyncIterator[StreamResponseChunk]:
        raise RuntimeError("chunk-error")
        yield  # pragma: no cover

    async def _chunk_failure_context_stream_async(
        self: llm.Model,
        *,
        ctx: llm.Context[Any],
        messages: list[Message],
        tools: object | None = None,
        format: object | None = None,
    ) -> AsyncContextStreamResponse[Any, None]:
        return AsyncContextStreamResponse(
            provider_id="openai",
            model_id="openai/gpt-4o-mini",
            provider_model_name="gpt-4o-mini:responses",
            params={},
            tools=None,
            format=None,
            input_messages=messages,
            chunk_iterator=_chunk_error_iterator(),
        )

    monkeypatch.setattr(
        instrument_module,
        "_ORIGINAL_MODEL_CONTEXT_STREAM_ASYNC",
        _chunk_failure_context_stream_async,
    )

    model = llm.Model(model_id="openai/gpt-4o-mini")
    ctx = llm.Context(deps={})
    messages: list[Message] = [llm.messages.user("hi")]

    with pytest.raises(RuntimeError, match="chunk-error"):
        response = await model.context_stream_async(ctx=ctx, messages=messages)
        await response.finish()

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
                "gen_ai.response.model": "openai/gpt-4o-mini",
                "gen_ai.response.finish_reasons": ["stop"],
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"hi"}]}]',
                "gen_ai.output.messages": '[{"role":"assistant","parts":[],"finish_reason":"stop"}]',
                "error.type": "RuntimeError",
                "error.message": "chunk-error",
            },
        }
    )
