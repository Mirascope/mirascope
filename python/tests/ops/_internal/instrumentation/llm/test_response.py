"""OpenTelemetry integration tests for Response.resume instrumentation."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from mirascope import llm, ops


@pytest.fixture(autouse=True, scope="function")
def initialize(tracer_provider: TracerProvider) -> Generator[None, None, None]:
    """Initialize ops configuration and LLM instrumentation for each test."""
    ops.configure(tracer_provider=tracer_provider)
    ops.instrument_llm()
    yield
    ops.uninstrument_llm()


@pytest.mark.vcr()
def test_response_resume_exports_mirascope_span(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test Mirascope instrumentation for Response.resume."""

    @llm.tool
    def get_weather(location: str) -> str:
        """Get the current weather for a location."""
        return f"Weather in {location}: 72°F, sunny"

    model = llm.Model(model_id="openai/gpt-4o-mini")
    messages = [llm.messages.user("What's the weather in Paris?")]

    response = model.call(messages, tools=[get_weather])
    assert response.tool_calls

    tool_outputs = response.execute_tools()
    resumed = response.resume(tool_outputs)

    assert resumed.content

    spans = span_exporter.get_finished_spans()
    # 3 spans: Model.call, Response.resume (Mirascope), Model.resume (GenAI)
    assert len(spans) == 3

    # Mirascope span is at index 2 (outer span finishes after inner GenAI span)
    mirascope_span = spans[2]
    assert "Response.resume" in mirascope_span.name
    assert mirascope_span.attributes is not None
    assert mirascope_span.attributes.get("mirascope.type") == "response_resume"
    assert (
        mirascope_span.attributes.get("mirascope.response.model_id")
        == "openai/gpt-4o-mini"
    )
    assert mirascope_span.attributes.get("mirascope.response.provider_id") == "openai"
    assert "mirascope.trace.output" in mirascope_span.attributes
    # Verify the pretty() output is captured
    trace_output = mirascope_span.attributes.get("mirascope.trace.output")
    assert isinstance(trace_output, str)
    assert "assistant" in trace_output.lower() or "weather" in trace_output.lower()


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_async_response_resume_exports_mirascope_span(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test Mirascope instrumentation for AsyncResponse.resume."""

    @llm.tool
    async def get_weather(location: str) -> str:
        """Get the current weather for a location."""
        return f"Weather in {location}: 72°F, sunny"

    model = llm.Model(model_id="openai/gpt-4o-mini")
    messages = [llm.messages.user("What's the weather in Rome?")]

    response = await model.call_async(messages, tools=[get_weather])
    assert response.tool_calls

    tool_outputs = await response.execute_tools()
    resumed = await response.resume(tool_outputs)

    assert resumed.content

    spans = span_exporter.get_finished_spans()
    # 3 spans: Model.call_async, AsyncResponse.resume (Mirascope), Model.resume_async (GenAI)
    assert len(spans) == 3

    # Mirascope span is at index 2 (outer span finishes after inner GenAI span)
    mirascope_span = spans[2]
    assert "AsyncResponse.resume" in mirascope_span.name
    assert mirascope_span.attributes is not None
    assert mirascope_span.attributes.get("mirascope.type") == "response_resume"
    assert (
        mirascope_span.attributes.get("mirascope.response.model_id")
        == "openai/gpt-4o-mini"
    )
    assert mirascope_span.attributes.get("mirascope.response.provider_id") == "openai"
    assert "mirascope.trace.output" in mirascope_span.attributes


@pytest.mark.vcr()
def test_stream_response_resume_exports_mirascope_span(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test Mirascope instrumentation for StreamResponse.resume."""

    @llm.tool
    def get_weather(location: str) -> str:
        """Get the current weather for a location."""
        return f"Weather in {location}: 72°F, sunny"

    model = llm.Model(model_id="openai/gpt-4o-mini")
    messages = [llm.messages.user("What's the weather in Madrid?")]

    response = model.stream(messages, tools=[get_weather])
    response.finish()
    assert response.tool_calls

    tool_outputs = response.execute_tools()
    resumed = response.resume(tool_outputs)
    resumed.finish()

    assert resumed.content

    spans = span_exporter.get_finished_spans()
    # 3 spans: Model.stream, StreamResponse.resume (Mirascope), Model.resume_stream (GenAI)
    assert len(spans) == 3

    # For streaming, Mirascope span finishes first (at index 1), GenAI finishes after stream consumed (at index 2)
    mirascope_span = spans[1]
    assert "StreamResponse.resume" in mirascope_span.name
    assert mirascope_span.attributes is not None
    assert mirascope_span.attributes.get("mirascope.type") == "response_resume"
    assert (
        mirascope_span.attributes.get("mirascope.response.model_id")
        == "openai/gpt-4o-mini"
    )
    assert mirascope_span.attributes.get("mirascope.response.provider_id") == "openai"
    assert "mirascope.trace.output" in mirascope_span.attributes


@pytest.mark.vcr()
def test_context_response_resume_exports_mirascope_span(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test Mirascope instrumentation for ContextResponse.resume."""

    @llm.tool
    def get_weather(location: str) -> str:
        """Get the current weather for a location."""
        return f"Weather in {location}: 72°F, sunny"

    model = llm.Model(model_id="openai/gpt-4o-mini")
    messages = [llm.messages.user("What's the weather in Vienna?")]
    ctx = llm.Context(deps=None)

    response = model.context_call(messages, ctx=ctx, tools=[get_weather])
    assert response.tool_calls

    tool_outputs = response.execute_tools(ctx)
    resumed = response.resume(ctx, tool_outputs)

    assert resumed.content

    spans = span_exporter.get_finished_spans()
    # 3 spans: Model.context_call, ContextResponse.resume (Mirascope), Model.context_resume (GenAI)
    assert len(spans) == 3

    # Mirascope span is at index 2 (outer span finishes after inner GenAI span)
    mirascope_span = spans[2]
    assert "ContextResponse.resume" in mirascope_span.name
    assert mirascope_span.attributes is not None
    assert mirascope_span.attributes.get("mirascope.type") == "response_resume"
    assert (
        mirascope_span.attributes.get("mirascope.response.model_id")
        == "openai/gpt-4o-mini"
    )
    assert mirascope_span.attributes.get("mirascope.response.provider_id") == "openai"
    assert "mirascope.trace.output" in mirascope_span.attributes


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_async_stream_response_resume_exports_mirascope_span(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test Mirascope instrumentation for AsyncStreamResponse.resume."""

    @llm.tool
    async def get_weather(location: str) -> str:
        """Get the current weather for a location."""
        return f"Weather in {location}: 72°F, sunny"

    model = llm.Model(model_id="openai/gpt-4o-mini")
    messages = [llm.messages.user("What's the weather in Berlin?")]

    response = await model.stream_async(messages, tools=[get_weather])
    await response.finish()
    assert response.tool_calls

    tool_outputs = await response.execute_tools()
    resumed = await response.resume(tool_outputs)
    await resumed.finish()

    assert resumed.content

    spans = span_exporter.get_finished_spans()
    # 3 spans: Model.stream_async, AsyncStreamResponse.resume (Mirascope), Model.resume_stream_async (GenAI)
    assert len(spans) == 3

    # For streaming, Mirascope span finishes first (at index 1), GenAI finishes after stream consumed (at index 2)
    mirascope_span = spans[1]
    assert "AsyncStreamResponse.resume" in mirascope_span.name
    assert mirascope_span.attributes is not None
    assert mirascope_span.attributes.get("mirascope.type") == "response_resume"
    assert (
        mirascope_span.attributes.get("mirascope.response.model_id")
        == "openai/gpt-4o-mini"
    )
    assert mirascope_span.attributes.get("mirascope.response.provider_id") == "openai"
    assert "mirascope.trace.output" in mirascope_span.attributes


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_async_context_response_resume_exports_mirascope_span(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test Mirascope instrumentation for AsyncContextResponse.resume."""

    @llm.tool
    async def get_weather(location: str) -> str:
        """Get the current weather for a location."""
        return f"Weather in {location}: 72°F, sunny"

    model = llm.Model(model_id="openai/gpt-4o-mini")
    messages = [llm.messages.user("What's the weather in Prague?")]
    ctx = llm.Context(deps=None)

    response = await model.context_call_async(messages, ctx=ctx, tools=[get_weather])
    assert response.tool_calls

    tool_outputs = await response.execute_tools(ctx)
    resumed = await response.resume(ctx, tool_outputs)

    assert resumed.content

    spans = span_exporter.get_finished_spans()
    # 3 spans: Model.context_call_async, AsyncContextResponse.resume (Mirascope), Model.context_resume_async (GenAI)
    assert len(spans) == 3

    # Mirascope span is at index 2 (outer span finishes after inner GenAI span)
    mirascope_span = spans[2]
    assert "AsyncContextResponse.resume" in mirascope_span.name
    assert mirascope_span.attributes is not None
    assert mirascope_span.attributes.get("mirascope.type") == "response_resume"
    assert (
        mirascope_span.attributes.get("mirascope.response.model_id")
        == "openai/gpt-4o-mini"
    )
    assert mirascope_span.attributes.get("mirascope.response.provider_id") == "openai"
    assert "mirascope.trace.output" in mirascope_span.attributes


@pytest.mark.vcr()
def test_context_stream_response_resume_exports_mirascope_span(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test Mirascope instrumentation for ContextStreamResponse.resume."""

    @llm.tool
    def get_weather(location: str) -> str:
        """Get the current weather for a location."""
        return f"Weather in {location}: 72°F, sunny"

    model = llm.Model(model_id="openai/gpt-4o-mini")
    messages = [llm.messages.user("What's the weather in Amsterdam?")]
    ctx = llm.Context(deps=None)

    response = model.context_stream(messages, ctx=ctx, tools=[get_weather])
    response.finish()
    assert response.tool_calls

    tool_outputs = response.execute_tools(ctx)
    resumed = response.resume(ctx, tool_outputs)
    resumed.finish()

    assert resumed.content

    spans = span_exporter.get_finished_spans()
    # 3 spans: Model.context_stream, ContextStreamResponse.resume (Mirascope), Model.context_resume_stream (GenAI)
    assert len(spans) == 3

    # For streaming, Mirascope span finishes first (at index 1), GenAI finishes after stream consumed (at index 2)
    mirascope_span = spans[1]
    assert "ContextStreamResponse.resume" in mirascope_span.name
    assert mirascope_span.attributes is not None
    assert mirascope_span.attributes.get("mirascope.type") == "response_resume"
    assert (
        mirascope_span.attributes.get("mirascope.response.model_id")
        == "openai/gpt-4o-mini"
    )
    assert mirascope_span.attributes.get("mirascope.response.provider_id") == "openai"
    assert "mirascope.trace.output" in mirascope_span.attributes


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_async_context_stream_response_resume_exports_mirascope_span(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test Mirascope instrumentation for AsyncContextStreamResponse.resume."""

    @llm.tool
    async def get_weather(location: str) -> str:
        """Get the current weather for a location."""
        return f"Weather in {location}: 72°F, sunny"

    model = llm.Model(model_id="openai/gpt-4o-mini")
    messages = [llm.messages.user("What's the weather in Brussels?")]
    ctx = llm.Context(deps=None)

    response = await model.context_stream_async(messages, ctx=ctx, tools=[get_weather])
    await response.finish()
    assert response.tool_calls

    tool_outputs = await response.execute_tools(ctx)
    resumed = await response.resume(ctx, tool_outputs)
    await resumed.finish()

    assert resumed.content

    spans = span_exporter.get_finished_spans()
    # 3 spans: Model.context_stream_async, AsyncContextStreamResponse.resume (Mirascope), Model.context_resume_stream_async (GenAI)
    assert len(spans) == 3

    # For streaming, Mirascope span finishes first (at index 1), GenAI finishes after stream consumed (at index 2)
    mirascope_span = spans[1]
    assert "AsyncContextStreamResponse.resume" in mirascope_span.name
    assert mirascope_span.attributes is not None
    assert mirascope_span.attributes.get("mirascope.type") == "response_resume"
    assert (
        mirascope_span.attributes.get("mirascope.response.model_id")
        == "openai/gpt-4o-mini"
    )
    assert mirascope_span.attributes.get("mirascope.response.provider_id") == "openai"
    assert "mirascope.trace.output" in mirascope_span.attributes
    assert "mirascope.trace.output" in mirascope_span.attributes
