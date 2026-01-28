"""OpenTelemetry integration tests for `llm.Model.resume*` methods."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any
from unittest.mock import Mock

import pytest
from inline_snapshot import snapshot
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from mirascope import llm, ops
from tests.ops.utils import span_snapshot


@pytest.fixture(autouse=True, scope="function")
def initialize(tracer_provider: TracerProvider) -> Generator[None, None, None]:
    """Initialize ops configuration and LLM instrumentation for each test."""
    ops.configure(tracer_provider=tracer_provider)
    ops.instrument_llm()
    yield
    ops.uninstrument_llm()


@pytest.mark.vcr()
def test_model_resume_exports_genai_span(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test OpenTelemetry instrumentation for Model.resume with tool outputs."""

    @llm.tool
    def get_weather(location: str) -> str:
        """Get the current weather for a location."""
        return f"Weather in {location}: 72°F, sunny"

    model = llm.Model(model_id="openai/gpt-4o-mini")
    messages = [llm.messages.user("What's the weather in Tokyo?")]

    # First call that triggers a tool call
    response = model.call(messages, tools=[get_weather])
    assert response.tool_calls

    # Execute tools and resume with tool outputs
    tool_outputs = response.execute_tools()
    resumed_response = response.resume(tool_outputs)

    assert resumed_response.content

    spans = span_exporter.get_finished_spans()
    # 3 spans: Model.call, Response.resume (Mirascope), Model.resume (GenAI)
    assert len(spans) == 3

    # Verify the GenAI span (from Model.resume) has correct attributes
    genai_span_dict = span_snapshot(spans[1])
    assert genai_span_dict == snapshot(
        {
            "name": "chat openai/gpt-4o-mini",
            "kind": "CLIENT",
            "status": "UNSET",
            "attributes": {
                "gen_ai.operation.name": "chat",
                "gen_ai.provider.name": "openai",
                "gen_ai.request.model": "openai/gpt-4o-mini",
                "gen_ai.output.type": "text",
                "gen_ai.tool.definitions": '[{"name":"get_weather","description":"Get the current weather for a location.","type":"function","parameters":{"properties":{"location":{"title":"Location","type":"string"}},"required":["location"],"additionalProperties":false,"$defs":null}}]',
                "gen_ai.response.model": "openai/gpt-4o-mini",
                "gen_ai.response.finish_reasons": ["stop"],
                "gen_ai.response.id": "resp_04369a7f101a58e40069701242f28081a286a7aedf808d875e",
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"What\'s the weather in Tokyo?"}]},{"role":"assistant","parts":[{"type":"tool_call","id":"call_CeSmJnilYrx5gzGCtEYJkUwC","name":"get_weather","arguments":{"location":"Tokyo"}}]},{"role":"user","parts":[{"type":"tool_call_response","id":"call_CeSmJnilYrx5gzGCtEYJkUwC","response":"Weather in Tokyo: 72°F, sunny"}]}]',
                "gen_ai.output.messages": '[{"role":"assistant","parts":[{"type":"text","content":"The current weather in Tokyo is 72°F and sunny."}],"finish_reason":"stop"}]',
                "gen_ai.usage.input_tokens": 80,
                "gen_ai.usage.output_tokens": 14,
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"What\'s the weather in Tokyo?"}],"name":null},{"role":"assistant","content":[{"type":"tool_call","id":"call_CeSmJnilYrx5gzGCtEYJkUwC","name":"get_weather","args":"{\\"location\\":\\"Tokyo\\"}"}],"name":null},{"role":"user","content":[{"type":"tool_output","id":"call_CeSmJnilYrx5gzGCtEYJkUwC","name":"get_weather","result":"Weather in Tokyo: 72°F, sunny"}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"The current weather in Tokyo is 72°F and sunny."}]',
                "mirascope.response.usage": '{"input_tokens":80,"output_tokens":14,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":94}',
            },
        }
    )


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_model_resume_async_exports_genai_span(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test OpenTelemetry instrumentation for Model.resume_async with tool outputs."""

    @llm.tool
    async def get_weather(location: str) -> str:
        """Get the current weather for a location."""
        return f"Weather in {location}: 72°F, sunny"

    model = llm.Model(model_id="openai/gpt-4o-mini")
    messages = [llm.messages.user("What's the weather in Paris?")]

    # First call that triggers a tool call
    response = await model.call_async(messages, tools=[get_weather])
    assert response.tool_calls

    # Execute tools and resume with tool outputs
    tool_outputs = await response.execute_tools()
    resumed_response = await response.resume(tool_outputs)

    assert resumed_response.content

    spans = span_exporter.get_finished_spans()
    # 3 spans: Model.call_async, AsyncResponse.resume (Mirascope), Model.resume_async (GenAI)
    assert len(spans) == 3

    genai_span_dict = span_snapshot(spans[1])
    assert genai_span_dict == snapshot(
        {
            "name": "chat openai/gpt-4o-mini",
            "kind": "CLIENT",
            "status": "UNSET",
            "attributes": {
                "gen_ai.operation.name": "chat",
                "gen_ai.provider.name": "openai",
                "gen_ai.request.model": "openai/gpt-4o-mini",
                "gen_ai.output.type": "text",
                "gen_ai.tool.definitions": '[{"name":"get_weather","description":"Get the current weather for a location.","type":"function","parameters":{"properties":{"location":{"title":"Location","type":"string"}},"required":["location"],"additionalProperties":false,"$defs":null}}]',
                "gen_ai.response.model": "openai/gpt-4o-mini",
                "gen_ai.response.finish_reasons": ["stop"],
                "gen_ai.response.id": "resp_0066a56981bdaccf00697014b9ec5c81939303be716778e26a",
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"What\'s the weather in Paris?"}]},{"role":"assistant","parts":[{"type":"tool_call","id":"call_ck0mvg6B86ddvfXFnWultLpX","name":"get_weather","arguments":{"location":"Paris"}}]},{"role":"user","parts":[{"type":"tool_call_response","id":"call_ck0mvg6B86ddvfXFnWultLpX","response":"Weather in Paris: 72°F, sunny"}]}]',
                "gen_ai.output.messages": '[{"role":"assistant","parts":[{"type":"text","content":"The weather in Paris is sunny with a temperature of 72°F."}],"finish_reason":"stop"}]',
                "gen_ai.usage.input_tokens": 80,
                "gen_ai.usage.output_tokens": 16,
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"What\'s the weather in Paris?"}],"name":null},{"role":"assistant","content":[{"type":"tool_call","id":"call_ck0mvg6B86ddvfXFnWultLpX","name":"get_weather","args":"{\\"location\\":\\"Paris\\"}"}],"name":null},{"role":"user","content":[{"type":"tool_output","id":"call_ck0mvg6B86ddvfXFnWultLpX","name":"get_weather","result":"Weather in Paris: 72°F, sunny"}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"The weather in Paris is sunny with a temperature of 72°F."}]',
                "mirascope.response.usage": '{"input_tokens":80,"output_tokens":16,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":96}',
            },
        }
    )


@pytest.mark.vcr()
def test_model_resume_stream_exports_genai_span(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test OpenTelemetry instrumentation for Model.resume_stream with tool outputs."""

    @llm.tool
    def get_weather(location: str) -> str:
        """Get the current weather for a location."""
        return f"Weather in {location}: 72°F, sunny"

    model = llm.Model(model_id="openai/gpt-4o-mini")
    messages = [llm.messages.user("What's the weather in London?")]

    # First call that triggers a tool call (use stream)
    response = model.stream(messages, tools=[get_weather])
    response.finish()
    assert response.tool_calls

    # Execute tools and resume with streaming
    tool_outputs = response.execute_tools()
    resumed_response = response.resume(tool_outputs)
    resumed_response.finish()

    assert resumed_response.content

    spans = span_exporter.get_finished_spans()
    # 3 spans: Model.stream, StreamResponse.resume (Mirascope), Model.resume_stream (GenAI)
    assert len(spans) == 3

    # For streaming, GenAI span is at index 2 (finishes after stream consumed)
    genai_span_dict = span_snapshot(spans[2])
    assert genai_span_dict == snapshot(
        {
            "name": "chat openai/gpt-4o-mini",
            "kind": "CLIENT",
            "status": "UNSET",
            "attributes": {
                "gen_ai.operation.name": "chat",
                "gen_ai.provider.name": "openai",
                "gen_ai.request.model": "openai/gpt-4o-mini",
                "gen_ai.output.type": "text",
                "gen_ai.tool.definitions": '[{"name":"get_weather","description":"Get the current weather for a location.","type":"function","parameters":{"properties":{"location":{"title":"Location","type":"string"}},"required":["location"],"additionalProperties":false,"$defs":null}}]',
                "gen_ai.response.model": "openai/gpt-4o-mini",
                "gen_ai.response.finish_reasons": ["stop"],
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"What\'s the weather in London?"}]},{"role":"assistant","parts":[{"type":"tool_call","id":"call_n6ENKpuZMXStFHYooHMIdkI1","name":"get_weather","arguments":{"location":"London"}}]},{"role":"user","parts":[{"type":"tool_call_response","id":"call_n6ENKpuZMXStFHYooHMIdkI1","response":"Weather in London: 72°F, sunny"}]}]',
                "gen_ai.output.messages": '[{"role":"assistant","parts":[{"type":"text","content":"The weather in London is sunny, with a temperature of 72°F."}],"finish_reason":"stop"}]',
                "gen_ai.usage.input_tokens": 80,
                "gen_ai.usage.output_tokens": 17,
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"What\'s the weather in London?"}],"name":null},{"role":"assistant","content":[{"type":"tool_call","id":"call_n6ENKpuZMXStFHYooHMIdkI1","name":"get_weather","args":"{\\"location\\":\\"London\\"}"}],"name":null},{"role":"user","content":[{"type":"tool_output","id":"call_n6ENKpuZMXStFHYooHMIdkI1","name":"get_weather","result":"Weather in London: 72°F, sunny"}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"The weather in London is sunny, with a temperature of 72°F."}]',
                "mirascope.response.usage": '{"input_tokens":80,"output_tokens":17,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":97}',
            },
        }
    )


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_model_resume_stream_async_exports_genai_span(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test OpenTelemetry instrumentation for Model.resume_stream_async with tool outputs."""

    @llm.tool
    async def get_weather(location: str) -> str:
        """Get the current weather for a location."""
        return f"Weather in {location}: 72°F, sunny"

    model = llm.Model(model_id="openai/gpt-4o-mini")
    messages = [llm.messages.user("What's the weather in Berlin?")]

    # First call that triggers a tool call (use async stream)
    response = await model.stream_async(messages, tools=[get_weather])
    await response.finish()
    assert response.tool_calls

    # Execute tools and resume with async streaming
    tool_outputs = await response.execute_tools()
    resumed_response = await response.resume(tool_outputs)
    await resumed_response.finish()

    assert resumed_response.content

    spans = span_exporter.get_finished_spans()
    # 3 spans: Model.stream_async, AsyncStreamResponse.resume (Mirascope), Model.resume_stream_async (GenAI)
    assert len(spans) == 3

    # For streaming, GenAI span is at index 2 (finishes after stream consumed)
    genai_span_dict = span_snapshot(spans[2])
    assert genai_span_dict == snapshot(
        {
            "name": "chat openai/gpt-4o-mini",
            "kind": "CLIENT",
            "status": "UNSET",
            "attributes": {
                "gen_ai.operation.name": "chat",
                "gen_ai.provider.name": "openai",
                "gen_ai.request.model": "openai/gpt-4o-mini",
                "gen_ai.output.type": "text",
                "gen_ai.tool.definitions": '[{"name":"get_weather","description":"Get the current weather for a location.","type":"function","parameters":{"properties":{"location":{"title":"Location","type":"string"}},"required":["location"],"additionalProperties":false,"$defs":null}}]',
                "gen_ai.response.model": "openai/gpt-4o-mini",
                "gen_ai.response.finish_reasons": ["stop"],
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"What\'s the weather in Berlin?"}]},{"role":"assistant","parts":[{"type":"tool_call","id":"call_kP2gia5asZ8fLNuJfLOEZqvD","name":"get_weather","arguments":{"location":"Berlin"}}]},{"role":"user","parts":[{"type":"tool_call_response","id":"call_kP2gia5asZ8fLNuJfLOEZqvD","response":"Weather in Berlin: 72°F, sunny"}]}]',
                "gen_ai.output.messages": '[{"role":"assistant","parts":[{"type":"text","content":"The weather in Berlin is currently 72°F and sunny."}],"finish_reason":"stop"}]',
                "gen_ai.usage.input_tokens": 80,
                "gen_ai.usage.output_tokens": 14,
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"What\'s the weather in Berlin?"}],"name":null},{"role":"assistant","content":[{"type":"tool_call","id":"call_kP2gia5asZ8fLNuJfLOEZqvD","name":"get_weather","args":"{\\"location\\":\\"Berlin\\"}"}],"name":null},{"role":"user","content":[{"type":"tool_output","id":"call_kP2gia5asZ8fLNuJfLOEZqvD","name":"get_weather","result":"Weather in Berlin: 72°F, sunny"}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"The weather in Berlin is currently 72°F and sunny."}]',
                "mirascope.response.usage": '{"input_tokens":80,"output_tokens":14,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":94}',
            },
        }
    )


@pytest.mark.vcr()
def test_model_context_resume_exports_genai_span(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test OpenTelemetry instrumentation for Model.context_resume with tool outputs."""

    @llm.tool
    def get_weather(location: str) -> str:
        """Get the current weather for a location."""
        return f"Weather in {location}: 72°F, sunny"

    model = llm.Model(model_id="openai/gpt-4o-mini")
    messages = [llm.messages.user("What's the weather in Sydney?")]
    ctx = llm.Context(deps=None)

    # First call that triggers a tool call
    response = model.context_call(messages, ctx=ctx, tools=[get_weather])
    assert response.tool_calls

    # Execute tools and resume with tool outputs
    tool_outputs = response.execute_tools(ctx)
    resumed_response = response.resume(ctx, tool_outputs)

    assert resumed_response.content

    spans = span_exporter.get_finished_spans()
    # 3 spans: Model.context_call, ContextResponse.resume (Mirascope), Model.context_resume (GenAI)
    assert len(spans) == 3

    genai_span_dict = span_snapshot(spans[1])
    assert genai_span_dict == snapshot(
        {
            "name": "chat openai/gpt-4o-mini",
            "kind": "CLIENT",
            "status": "UNSET",
            "attributes": {
                "gen_ai.operation.name": "chat",
                "gen_ai.provider.name": "openai",
                "gen_ai.request.model": "openai/gpt-4o-mini",
                "gen_ai.output.type": "text",
                "gen_ai.tool.definitions": '[{"name":"get_weather","description":"Get the current weather for a location.","type":"function","parameters":{"properties":{"location":{"title":"Location","type":"string"}},"required":["location"],"additionalProperties":false,"$defs":null}}]',
                "gen_ai.response.model": "openai/gpt-4o-mini",
                "gen_ai.response.finish_reasons": ["stop"],
                "gen_ai.response.id": "resp_0e27fad540c1fc6c00697014c1bda081a3bf1984b0d5b5ff24",
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"What\'s the weather in Sydney?"}]},{"role":"assistant","parts":[{"type":"tool_call","id":"call_WaUuUqAuyaPXEDenDhDiTT86","name":"get_weather","arguments":{"location":"Sydney"}}]},{"role":"user","parts":[{"type":"tool_call_response","id":"call_WaUuUqAuyaPXEDenDhDiTT86","response":"Weather in Sydney: 72°F, sunny"}]}]',
                "gen_ai.output.messages": '[{"role":"assistant","parts":[{"type":"text","content":"The weather in Sydney is currently 72°F and sunny."}],"finish_reason":"stop"}]',
                "gen_ai.usage.input_tokens": 80,
                "gen_ai.usage.output_tokens": 14,
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"What\'s the weather in Sydney?"}],"name":null},{"role":"assistant","content":[{"type":"tool_call","id":"call_WaUuUqAuyaPXEDenDhDiTT86","name":"get_weather","args":"{\\"location\\":\\"Sydney\\"}"}],"name":null},{"role":"user","content":[{"type":"tool_output","id":"call_WaUuUqAuyaPXEDenDhDiTT86","name":"get_weather","result":"Weather in Sydney: 72°F, sunny"}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"The weather in Sydney is currently 72°F and sunny."}]',
                "mirascope.response.usage": '{"input_tokens":80,"output_tokens":14,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":94}',
            },
        }
    )


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_model_context_resume_async_exports_genai_span(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test OpenTelemetry instrumentation for Model.context_resume_async with tool outputs."""

    @llm.tool
    async def get_weather(location: str) -> str:
        """Get the current weather for a location."""
        return f"Weather in {location}: 72°F, sunny"

    model = llm.Model(model_id="openai/gpt-4o-mini")
    messages = [llm.messages.user("What's the weather in Toronto?")]
    ctx = llm.Context(deps=None)

    # First call that triggers a tool call
    response = await model.context_call_async(messages, ctx=ctx, tools=[get_weather])
    assert response.tool_calls

    # Execute tools and resume with tool outputs
    tool_outputs = await response.execute_tools(ctx)
    resumed_response = await response.resume(ctx, tool_outputs)

    assert resumed_response.content

    spans = span_exporter.get_finished_spans()
    # 3 spans: Model.context_call_async, AsyncContextResponse.resume (Mirascope), Model.context_resume_async (GenAI)
    assert len(spans) == 3

    genai_span_dict = span_snapshot(spans[1])
    assert genai_span_dict == snapshot(
        {
            "name": "chat openai/gpt-4o-mini",
            "kind": "CLIENT",
            "status": "UNSET",
            "attributes": {
                "gen_ai.operation.name": "chat",
                "gen_ai.provider.name": "openai",
                "gen_ai.request.model": "openai/gpt-4o-mini",
                "gen_ai.output.type": "text",
                "gen_ai.tool.definitions": '[{"name":"get_weather","description":"Get the current weather for a location.","type":"function","parameters":{"properties":{"location":{"title":"Location","type":"string"}},"required":["location"],"additionalProperties":false,"$defs":null}}]',
                "gen_ai.response.model": "openai/gpt-4o-mini",
                "gen_ai.response.finish_reasons": ["stop"],
                "gen_ai.response.id": "resp_0bc7942ee17daaed00697014c4875881a3a34bb7c20800b278",
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"What\'s the weather in Toronto?"}]},{"role":"assistant","parts":[{"type":"tool_call","id":"call_kOQZ6ugCR9mv9T22cullWbcx","name":"get_weather","arguments":{"location":"Toronto"}}]},{"role":"user","parts":[{"type":"tool_call_response","id":"call_kOQZ6ugCR9mv9T22cullWbcx","response":"Weather in Toronto: 72°F, sunny"}]}]',
                "gen_ai.output.messages": '[{"role":"assistant","parts":[{"type":"text","content":"The weather in Toronto is 72°F and sunny."}],"finish_reason":"stop"}]',
                "gen_ai.usage.input_tokens": 80,
                "gen_ai.usage.output_tokens": 13,
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"What\'s the weather in Toronto?"}],"name":null},{"role":"assistant","content":[{"type":"tool_call","id":"call_kOQZ6ugCR9mv9T22cullWbcx","name":"get_weather","args":"{\\"location\\":\\"Toronto\\"}"}],"name":null},{"role":"user","content":[{"type":"tool_output","id":"call_kOQZ6ugCR9mv9T22cullWbcx","name":"get_weather","result":"Weather in Toronto: 72°F, sunny"}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"The weather in Toronto is 72°F and sunny."}]',
                "mirascope.response.usage": '{"input_tokens":80,"output_tokens":13,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":93}',
            },
        }
    )


@pytest.mark.vcr()
def test_model_context_resume_stream_exports_genai_span(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test OpenTelemetry instrumentation for Model.context_resume_stream with tool outputs."""

    @llm.tool
    def get_weather(location: str) -> str:
        """Get the current weather for a location."""
        return f"Weather in {location}: 72°F, sunny"

    model = llm.Model(model_id="openai/gpt-4o-mini")
    messages = [llm.messages.user("What's the weather in Mumbai?")]
    ctx = llm.Context(deps=None)

    # First call that triggers a tool call (use context stream)
    response = model.context_stream(messages, ctx=ctx, tools=[get_weather])
    response.finish()
    assert response.tool_calls

    # Execute tools and resume with context streaming
    tool_outputs = response.execute_tools(ctx)
    resumed_response = response.resume(ctx, tool_outputs)
    resumed_response.finish()

    assert resumed_response.content

    spans = span_exporter.get_finished_spans()
    # 3 spans: Model.context_stream, ContextStreamResponse.resume (Mirascope), Model.context_resume_stream (GenAI)
    assert len(spans) == 3

    # For streaming, GenAI span is at index 2 (finishes after stream consumed)
    genai_span_dict = span_snapshot(spans[2])
    assert genai_span_dict == snapshot(
        {
            "name": "chat openai/gpt-4o-mini",
            "kind": "CLIENT",
            "status": "UNSET",
            "attributes": {
                "gen_ai.operation.name": "chat",
                "gen_ai.provider.name": "openai",
                "gen_ai.request.model": "openai/gpt-4o-mini",
                "gen_ai.output.type": "text",
                "gen_ai.tool.definitions": '[{"name":"get_weather","description":"Get the current weather for a location.","type":"function","parameters":{"properties":{"location":{"title":"Location","type":"string"}},"required":["location"],"additionalProperties":false,"$defs":null}}]',
                "gen_ai.response.model": "openai/gpt-4o-mini",
                "gen_ai.response.finish_reasons": ["stop"],
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"What\'s the weather in Mumbai?"}]},{"role":"assistant","parts":[{"type":"tool_call","id":"call_D3VTNzxwSAaUHBRiNLeJudFA","name":"get_weather","arguments":{"location":"Mumbai"}}]},{"role":"user","parts":[{"type":"tool_call_response","id":"call_D3VTNzxwSAaUHBRiNLeJudFA","response":"Weather in Mumbai: 72°F, sunny"}]}]',
                "gen_ai.output.messages": '[{"role":"assistant","parts":[{"type":"text","content":"The weather in Mumbai is currently 72°F and sunny."}],"finish_reason":"stop"}]',
                "gen_ai.usage.input_tokens": 80,
                "gen_ai.usage.output_tokens": 14,
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"What\'s the weather in Mumbai?"}],"name":null},{"role":"assistant","content":[{"type":"tool_call","id":"call_D3VTNzxwSAaUHBRiNLeJudFA","name":"get_weather","args":"{\\"location\\":\\"Mumbai\\"}"}],"name":null},{"role":"user","content":[{"type":"tool_output","id":"call_D3VTNzxwSAaUHBRiNLeJudFA","name":"get_weather","result":"Weather in Mumbai: 72°F, sunny"}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"The weather in Mumbai is currently 72°F and sunny."}]',
                "mirascope.response.usage": '{"input_tokens":80,"output_tokens":14,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":94}',
            },
        }
    )


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_model_context_resume_stream_async_exports_genai_span(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test OpenTelemetry instrumentation for Model.context_resume_stream_async with tool outputs."""

    @llm.tool
    async def get_weather(location: str) -> str:
        """Get the current weather for a location."""
        return f"Weather in {location}: 72°F, sunny"

    model = llm.Model(model_id="openai/gpt-4o-mini")
    messages = [llm.messages.user("What's the weather in Cairo?")]
    ctx = llm.Context(deps=None)

    # First call that triggers a tool call (use async context stream)
    response = await model.context_stream_async(messages, ctx=ctx, tools=[get_weather])
    await response.finish()
    assert response.tool_calls

    # Execute tools and resume with async context streaming
    tool_outputs = await response.execute_tools(ctx)
    resumed_response = await response.resume(ctx, tool_outputs)
    await resumed_response.finish()

    assert resumed_response.content

    spans = span_exporter.get_finished_spans()
    # 3 spans: Model.context_stream_async, AsyncContextStreamResponse.resume (Mirascope), Model.context_resume_stream_async (GenAI)
    assert len(spans) == 3

    # For streaming, GenAI span is at index 2 (finishes after stream consumed)
    genai_span_dict = span_snapshot(spans[2])
    assert genai_span_dict == snapshot(
        {
            "name": "chat openai/gpt-4o-mini",
            "kind": "CLIENT",
            "status": "UNSET",
            "attributes": {
                "gen_ai.operation.name": "chat",
                "gen_ai.provider.name": "openai",
                "gen_ai.request.model": "openai/gpt-4o-mini",
                "gen_ai.output.type": "text",
                "gen_ai.tool.definitions": '[{"name":"get_weather","description":"Get the current weather for a location.","type":"function","parameters":{"properties":{"location":{"title":"Location","type":"string"}},"required":["location"],"additionalProperties":false,"$defs":null}}]',
                "gen_ai.response.model": "openai/gpt-4o-mini",
                "gen_ai.response.finish_reasons": ["stop"],
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"What\'s the weather in Cairo?"}]},{"role":"assistant","parts":[{"type":"tool_call","id":"call_eg35cztygTdIOnJ7l1Ux1wHT","name":"get_weather","arguments":{"location":"Cairo"}}]},{"role":"user","parts":[{"type":"tool_call_response","id":"call_eg35cztygTdIOnJ7l1Ux1wHT","response":"Weather in Cairo: 72°F, sunny"}]}]',
                "gen_ai.output.messages": '[{"role":"assistant","parts":[{"type":"text","content":"The weather in Cairo is currently 72°F and sunny."}],"finish_reason":"stop"}]',
                "gen_ai.usage.input_tokens": 81,
                "gen_ai.usage.output_tokens": 14,
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"What\'s the weather in Cairo?"}],"name":null},{"role":"assistant","content":[{"type":"tool_call","id":"call_eg35cztygTdIOnJ7l1Ux1wHT","name":"get_weather","args":"{\\"location\\":\\"Cairo\\"}"}],"name":null},{"role":"user","content":[{"type":"tool_output","id":"call_eg35cztygTdIOnJ7l1Ux1wHT","name":"get_weather","result":"Weather in Cairo: 72°F, sunny"}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"The weather in Cairo is currently 72°F and sunny."}]',
                "mirascope.response.usage": '{"input_tokens":81,"output_tokens":14,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":95}',
            },
        }
    )


def test_model_resume_stream_without_tracer_returns_response(
    span_exporter: InMemorySpanExporter, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that resume_stream returns response when tracer is None."""
    from mirascope.ops._internal.configuration import set_tracer
    from mirascope.ops._internal.instrumentation.llm import model as instrument_module

    set_tracer(None)
    dummy_response = object()

    def _fake_resume_stream(
        self: llm.Model,
        *,
        response: llm.StreamResponse[Any],
        content: llm.UserContent,
    ) -> object:
        return dummy_response

    monkeypatch.setattr(
        instrument_module, "_ORIGINAL_MODEL_RESUME_STREAM", _fake_resume_stream
    )

    model = llm.Model(model_id="openai/gpt-4o-mini")
    fake_stream_response = Mock(spec=llm.StreamResponse)
    fake_stream_response.messages = [llm.messages.user("hi")]
    fake_stream_response.toolkit = None
    fake_stream_response.format = None

    result = model.resume_stream(response=fake_stream_response, content="test")

    assert result is dummy_response
    assert span_exporter.get_finished_spans() == ()


def test_model_resume_stream_records_error_on_exception(
    span_exporter: InMemorySpanExporter, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that resume_stream records error when original method raises."""
    from mirascope.ops._internal.instrumentation.llm import model as instrument_module

    def _failing_resume_stream(
        self: llm.Model,
        *,
        response: llm.StreamResponse[Any],
        content: llm.UserContent,
    ) -> object:
        raise ValueError("resume stream error")

    monkeypatch.setattr(
        instrument_module, "_ORIGINAL_MODEL_RESUME_STREAM", _failing_resume_stream
    )

    model = llm.Model(model_id="openai/gpt-4o-mini")
    fake_stream_response = Mock(spec=llm.StreamResponse)
    fake_stream_response.messages = [llm.messages.user("hi")]
    fake_stream_response.toolkit = None
    fake_stream_response.format = None

    with pytest.raises(ValueError, match="resume stream error"):
        model.resume_stream(response=fake_stream_response, content="test")

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    assert spans[0].status.status_code.name == "ERROR"


@pytest.mark.asyncio
async def test_model_resume_stream_async_without_tracer_returns_response(
    span_exporter: InMemorySpanExporter, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that resume_stream_async returns response when tracer is None."""
    from mirascope.ops._internal.configuration import set_tracer
    from mirascope.ops._internal.instrumentation.llm import model as instrument_module

    set_tracer(None)
    dummy_response = object()

    async def _fake_resume_stream_async(
        self: llm.Model,
        *,
        response: llm.AsyncStreamResponse[Any],
        content: llm.UserContent,
    ) -> object:
        return dummy_response

    monkeypatch.setattr(
        instrument_module,
        "_ORIGINAL_MODEL_RESUME_STREAM_ASYNC",
        _fake_resume_stream_async,
    )

    model = llm.Model(model_id="openai/gpt-4o-mini")
    fake_stream_response = Mock(spec=llm.AsyncStreamResponse)
    fake_stream_response.messages = [llm.messages.user("hi")]
    fake_stream_response.toolkit = None
    fake_stream_response.format = None

    result = await model.resume_stream_async(
        response=fake_stream_response, content="test"
    )

    assert result is dummy_response
    assert span_exporter.get_finished_spans() == ()


@pytest.mark.asyncio
async def test_model_resume_stream_async_records_error_on_exception(
    span_exporter: InMemorySpanExporter, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that resume_stream_async records error when original method raises."""
    from mirascope.ops._internal.instrumentation.llm import model as instrument_module

    async def _failing_resume_stream_async(
        self: llm.Model,
        *,
        response: llm.AsyncStreamResponse[Any],
        content: llm.UserContent,
    ) -> object:
        raise ValueError("async resume stream error")

    monkeypatch.setattr(
        instrument_module,
        "_ORIGINAL_MODEL_RESUME_STREAM_ASYNC",
        _failing_resume_stream_async,
    )

    model = llm.Model(model_id="openai/gpt-4o-mini")
    fake_stream_response = Mock(spec=llm.AsyncStreamResponse)
    fake_stream_response.messages = [llm.messages.user("hi")]
    fake_stream_response.toolkit = None
    fake_stream_response.format = None

    with pytest.raises(ValueError, match="async resume stream error"):
        await model.resume_stream_async(response=fake_stream_response, content="test")

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    assert spans[0].status.status_code.name == "ERROR"


def test_model_context_resume_stream_without_tracer_returns_response(
    span_exporter: InMemorySpanExporter, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that context_resume_stream returns response when tracer is None."""
    from mirascope.ops._internal.configuration import set_tracer
    from mirascope.ops._internal.instrumentation.llm import model as instrument_module

    set_tracer(None)
    dummy_response = object()

    def _fake_context_resume_stream(
        self: llm.Model,
        *,
        ctx: llm.Context[Any],
        response: llm.ContextStreamResponse[Any, Any],
        content: llm.UserContent,
    ) -> object:
        return dummy_response

    monkeypatch.setattr(
        instrument_module,
        "_ORIGINAL_MODEL_CONTEXT_RESUME_STREAM",
        _fake_context_resume_stream,
    )

    model = llm.Model(model_id="openai/gpt-4o-mini")
    ctx = llm.Context(deps=None)
    fake_stream_response = Mock(spec=llm.ContextStreamResponse)
    fake_stream_response.messages = [llm.messages.user("hi")]
    fake_stream_response.toolkit = None
    fake_stream_response.format = None

    result = model.context_resume_stream(
        ctx=ctx, response=fake_stream_response, content="test"
    )

    assert result is dummy_response
    assert span_exporter.get_finished_spans() == ()


def test_model_context_resume_stream_records_error_on_exception(
    span_exporter: InMemorySpanExporter, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that context_resume_stream records error when original method raises."""
    from mirascope.ops._internal.instrumentation.llm import model as instrument_module

    def _failing_context_resume_stream(
        self: llm.Model,
        *,
        ctx: llm.Context[Any],
        response: llm.ContextStreamResponse[Any, Any],
        content: llm.UserContent,
    ) -> object:
        raise ValueError("context resume stream error")

    monkeypatch.setattr(
        instrument_module,
        "_ORIGINAL_MODEL_CONTEXT_RESUME_STREAM",
        _failing_context_resume_stream,
    )

    model = llm.Model(model_id="openai/gpt-4o-mini")
    ctx = llm.Context(deps=None)
    fake_stream_response = Mock(spec=llm.ContextStreamResponse)
    fake_stream_response.messages = [llm.messages.user("hi")]
    fake_stream_response.toolkit = None
    fake_stream_response.format = None

    with pytest.raises(ValueError, match="context resume stream error"):
        model.context_resume_stream(
            ctx=ctx, response=fake_stream_response, content="test"
        )

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    assert spans[0].status.status_code.name == "ERROR"


@pytest.mark.asyncio
async def test_model_context_resume_stream_async_without_tracer_returns_response(
    span_exporter: InMemorySpanExporter, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that context_resume_stream_async returns response when tracer is None."""
    from mirascope.ops._internal.configuration import set_tracer
    from mirascope.ops._internal.instrumentation.llm import model as instrument_module

    set_tracer(None)
    dummy_response = object()

    async def _fake_context_resume_stream_async(
        self: llm.Model,
        *,
        ctx: llm.Context[Any],
        response: llm.AsyncContextStreamResponse[Any, Any],
        content: llm.UserContent,
    ) -> object:
        return dummy_response

    monkeypatch.setattr(
        instrument_module,
        "_ORIGINAL_MODEL_CONTEXT_RESUME_STREAM_ASYNC",
        _fake_context_resume_stream_async,
    )

    model = llm.Model(model_id="openai/gpt-4o-mini")
    ctx = llm.Context(deps=None)
    fake_stream_response = Mock(spec=llm.AsyncContextStreamResponse)
    fake_stream_response.messages = [llm.messages.user("hi")]
    fake_stream_response.toolkit = None
    fake_stream_response.format = None

    result = await model.context_resume_stream_async(
        ctx=ctx, response=fake_stream_response, content="test"
    )

    assert result is dummy_response
    assert span_exporter.get_finished_spans() == ()


@pytest.mark.asyncio
async def test_model_context_resume_stream_async_records_error_on_exception(
    span_exporter: InMemorySpanExporter, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that context_resume_stream_async records error when original method raises."""
    from mirascope.ops._internal.instrumentation.llm import model as instrument_module

    async def _failing_context_resume_stream_async(
        self: llm.Model,
        *,
        ctx: llm.Context[Any],
        response: llm.AsyncContextStreamResponse[Any, Any],
        content: llm.UserContent,
    ) -> object:
        raise ValueError("async context resume stream error")

    monkeypatch.setattr(
        instrument_module,
        "_ORIGINAL_MODEL_CONTEXT_RESUME_STREAM_ASYNC",
        _failing_context_resume_stream_async,
    )

    model = llm.Model(model_id="openai/gpt-4o-mini")
    ctx = llm.Context(deps=None)
    fake_stream_response = Mock(spec=llm.AsyncContextStreamResponse)
    fake_stream_response.messages = [llm.messages.user("hi")]
    fake_stream_response.toolkit = None
    fake_stream_response.format = None

    with pytest.raises(ValueError, match="async context resume stream error"):
        await model.context_resume_stream_async(
            ctx=ctx, response=fake_stream_response, content="test"
        )

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    assert spans[0].status.status_code.name == "ERROR"
