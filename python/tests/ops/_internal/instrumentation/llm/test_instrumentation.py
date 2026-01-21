"""Tests for LLM instrumentation control (instrument/uninstrument, tracer context)."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

from mirascope import llm, ops
from mirascope.ops._internal import configuration as ops_configuration
from mirascope.ops._internal.configuration import set_tracer


@pytest.fixture(autouse=True, scope="function")
def initialize(tracer_provider: TracerProvider) -> Generator[None, None, None]:
    """Initialize ops configuration and LLM instrumentation for each test."""
    ops.configure(tracer_provider=tracer_provider)
    ops.instrument_llm()
    yield
    ops.uninstrument_llm()


def test_uninstrument_llm() -> None:
    """Test uninstrumentation and re-instrumentation is idempotent."""
    ops.uninstrument_llm()

    ops.instrument_llm()
    first_call = llm.Model.call
    ops.instrument_llm()
    assert llm.Model.call is first_call

    ops.uninstrument_llm()


@pytest.mark.vcr()
def test_model_call_without_instrumentation(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that model.call works without instrumentation (no spans created)."""
    ops.uninstrument_llm()

    model = llm.Model(model_id="openai/gpt-4o-mini")
    messages = [llm.messages.user("Hello")]

    response = model.call(messages)

    assert response.content
    spans = span_exporter.get_finished_spans()
    assert len(spans) == 0


@pytest.mark.vcr()
def test_model_call_with_tracer_set_to_none(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that span() returns None when tracer is explicitly set to None."""
    set_tracer(None)

    model = llm.Model(model_id="openai/gpt-4o-mini")
    messages = [llm.messages.user("Test with None tracer")]

    response = model.call(messages)

    assert response.content
    spans = span_exporter.get_finished_spans()
    assert len(spans) == 0


def test_tracer_context_temporarily_sets_tracer(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that tracer_context temporarily sets a tracer and restores the previous."""
    original_tracer = ops_configuration.get_tracer()

    provider = TracerProvider()
    new_tracer = provider.get_tracer("test-tracer")

    with ops.tracer_context(new_tracer) as ctx_tracer:
        assert ctx_tracer is new_tracer
        assert ops_configuration.get_tracer() is new_tracer

    assert ops_configuration.get_tracer() is original_tracer


@pytest.mark.vcr()
def test_tracer_context_with_model_call(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that tracer_context works with model calls."""
    model = llm.Model(model_id="openai/gpt-4o-mini")
    messages = [llm.messages.user("Say hello")]

    with ops.tracer_context(None):
        response = model.call(messages)
        assert response.content

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 0
