"""OpenTelemetry integration tests for `llm.Model.context_call_async`."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from inline_snapshot import snapshot
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

from mirascope import llm, ops
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
async def test_model_context_call_async_exports_genai_span(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test OpenTelemetry instrumentation with context."""
    model = llm.Model(model_id="openai/gpt-4o-mini")
    ctx = llm.Context(deps={"tenant": "kai"})
    messages = [
        llm.messages.system("You are a concise assistant."),
        llm.messages.user("Say hello to the user named Kai."),
    ]

    response = await model.context_call_async(ctx=ctx, messages=messages)
    assert "Kai" in response.pretty()

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
                "gen_ai.response.id": "resp_03b58d3d78b0728c00691ae8bae894819787eb587c899f106d",
                "gen_ai.system_instructions": '[{"type":"text","content":"You are a concise assistant."}]',
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"Say hello to the user named Kai."}]}]',
                "gen_ai.output.messages": '[{"role":"assistant","parts":[{"type":"text","content":"Hello, Kai! How can I assist you today?"}],"finish_reason":"stop"}]',
            },
        }
    )
