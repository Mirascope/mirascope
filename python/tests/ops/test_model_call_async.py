"""OpenTelemetry integration tests for `llm.Model.call_async`."""

from __future__ import annotations

from collections.abc import Generator, Mapping
from typing import Any, cast

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
async def test_model_call_async_exports_genai_span(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that streaming a model call exports the correct OpenTelemetry span."""
    model = llm.Model(model_id="openai/gpt-4o-mini")
    messages = [
        llm.messages.system("You are a concise assistant."),
        llm.messages.user("Say hello to the user named Kai."),
    ]

    response = await model.call_async(messages=messages)
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
                "gen_ai.response.id": "resp_0f1e4ac77eea3e0a00691ae34d8be88194abe8a570acf9152b",
                "gen_ai.system_instructions": '[{"type":"text","content":"You are a concise assistant."}]',
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"Say hello to the user named Kai."}]}]',
                "gen_ai.output.messages": '[{"role":"assistant","parts":[{"type":"text","content":"Hello, Kai! How can I assist you today?"}],"finish_reason":"stop"}]',
            },
        }
    )


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_model_call_async_records_untracked_params_event(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Ensure unsupported params are preserved via OTLP events instead of dropped."""

    class _NonSerializable:
        """Dummy object that stringifies cleanly for untracked params tests."""

        def __str__(self) -> str:
            return "custom-param"

    class _BadStr:
        """Dummy object whose __str__ returns a non-str for error coverage."""

        def __str__(self) -> Any:  # noqa: ANN401
            return 123

    extra_params = cast(
        dict[str, object],
        {
            "metadata": {"trace": {"id": "abc123", "tags": ["otel"]}},
            "unsupported_list": [1, 2, 3],
            "non_serializable": _NonSerializable(),
            "bad_str": _BadStr(),
        },
    )
    model = llm.Model(
        model_id="openai/gpt-4o-mini",
        **cast(Any, extra_params),
    )
    messages = [
        llm.messages.system("You are a concise assistant."),
        llm.messages.user("Say hello to the user named Kai."),
    ]

    await model.call_async(messages=messages)

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    events = spans[0].events
    assert events, "Expected at least one span event"
    event = events[-1]

    event_attributes = cast(Mapping[str, object], event.attributes or {})
    event_snapshot = {
        "name": event.name,
        "attributes": {
            key: list(value) if isinstance(value, tuple) else value
            for key, value in event_attributes.items()
        },
    }
    assert event_snapshot == snapshot(
        {
            "name": "gen_ai.request.params.untracked",
            "attributes": {
                "gen_ai.untracked_params.count": 4,
                "gen_ai.untracked_params.keys": [
                    "metadata",
                    "unsupported_list",
                    "non_serializable",
                    "bad_str",
                ],
                "gen_ai.untracked_params.json": '{"metadata":{"trace":{"id":"abc123","tags":["otel"]}},"unsupported_list":[1,2,3],"non_serializable":"custom-param","bad_str":"<_BadStr>"}',
            },
        }
    )
