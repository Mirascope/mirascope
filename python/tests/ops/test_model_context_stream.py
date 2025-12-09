"""OpenTelemetry integration tests for `llm.Model.context_stream`."""

from __future__ import annotations

from collections.abc import Generator, Sequence
from typing import Any

import pytest
from inline_snapshot import snapshot
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

from mirascope import llm, ops
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
def test_model_context_stream_exports_genai_span(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that streaming a model call exports the correct OpenTelemetry span."""
    model = llm.Model(model_id="openai/gpt-4o-mini")
    ctx = llm.Context(deps={"tenant": "kai"})
    messages = [
        llm.messages.system("You are a concise assistant."),
        llm.messages.user("Say hello to the user named Kai."),
    ]

    response = model.context_stream(ctx=ctx, messages=messages)
    response.finish()

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


def test_model_context_stream_without_tracer_returns_response(
    span_exporter: InMemorySpanExporter, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that streaming a model call returns the response object."""
    set_tracer(None)
    dummy_response = object()

    def _fake_context_stream(
        self: llm.Model,
        *,
        ctx: llm.Context[Any],
        messages: Sequence[llm.Message],
        tools: object | None = None,
        format: object | None = None,
    ) -> object:
        return dummy_response

    monkeypatch.setattr(
        instrument_module, "_ORIGINAL_MODEL_CONTEXT_STREAM", _fake_context_stream
    )

    model = llm.Model(model_id="openai/gpt-4o-mini")
    ctx = llm.Context(deps={})
    messages = [llm.messages.user("hi")]

    response = model.context_stream(ctx=ctx, messages=messages)

    assert response is dummy_response
    assert span_exporter.get_finished_spans() == ()


def test_model_context_stream_records_error_on_exception(
    span_exporter: InMemorySpanExporter, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that streaming a model call exports the correct OpenTelemetry span."""

    def _failing_context_stream(
        self: llm.Model,
        *,
        ctx: llm.Context[Any],
        messages: Sequence[llm.Message],
        tools: object | None = None,
        format: object | None = None,
    ) -> object:
        raise ValueError("error")

    monkeypatch.setattr(
        instrument_module, "_ORIGINAL_MODEL_CONTEXT_STREAM", _failing_context_stream
    )

    model = llm.Model(model_id="openai/gpt-4o-mini")
    ctx = llm.Context(deps={})
    messages = [llm.messages.user("hi")]

    with pytest.raises(ValueError, match="error"):
        model.context_stream(ctx=ctx, messages=messages)

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
