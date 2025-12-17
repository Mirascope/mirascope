"""OpenTelemetry integration test for `llm.Model.call`."""

from __future__ import annotations

import json
from collections.abc import Generator, Mapping, Sequence
from pathlib import Path
from typing import Any, cast
from unittest.mock import Mock

import httpx
import openai
import pytest
from inline_snapshot import snapshot
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)
from pydantic import BaseModel

from mirascope import llm, ops
from mirascope.llm import Text
from mirascope.llm.content import (
    Audio,
    Base64ImageSource,
    Image,
)
from mirascope.llm.providers.provider_registry import PROVIDER_REGISTRY
from mirascope.llm.responses.finish_reason import FinishReason
from mirascope.ops._internal import configuration as ops_configuration
from mirascope.ops._internal.configuration import set_tracer
from tests.ops.utils import span_snapshot


class Book(BaseModel):
    """A book with title and author."""

    title: str
    author: str


@pytest.fixture(autouse=True, scope="function")
def reset_provider_registry() -> Generator[None, None, None]:
    """Reset the provider registry before and after each test."""
    PROVIDER_REGISTRY.clear()
    yield
    PROVIDER_REGISTRY.clear()


@pytest.fixture(autouse=True, scope="function")
def initialize() -> Generator[None, None, None]:
    """Initialize ops configuration and LLM instrumentation for each test."""
    ops.configure()
    ops.instrument_llm()
    yield
    ops.uninstrument_llm()


@pytest.mark.vcr()
def test_model_call_exports_genai_span(span_exporter: InMemorySpanExporter) -> None:
    """Test OpenTelemetry instrumentation with basic model call."""
    model = llm.Model(model_id="openai/gpt-4o-mini")
    messages = [
        llm.messages.system("You are a concise assistant."),
        llm.messages.user("Say hello to the user named Kai."),
    ]

    response = model.call(messages=messages)
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
                "gen_ai.response.id": "resp_07cda32f3bb965f500691448c25b8481939254851481fbd88e",
                "gen_ai.system_instructions": '[{"type":"text","content":"You are a concise assistant."}]',
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"Say hello to the user named Kai."}]}]',
                "gen_ai.output.messages": '[{"role":"assistant","parts":[{"type":"text","content":"Hello, Kai!"}],"finish_reason":"stop"}]',
            },
        }
    )


@pytest.mark.vcr()
def test_model_call_with_tools(span_exporter: InMemorySpanExporter) -> None:
    """Test OpenTelemetry instrumentation with tool calling."""

    @llm.tool
    def get_current_weather(location: str, unit: str = "fahrenheit") -> str:
        """Get the current weather in a given location."""
        return f"Weather in {location}: 72°{unit[0].upper()}, sunny"

    model = llm.Model(model_id="openai/gpt-4o-mini")
    messages = [llm.messages.user("What's the weather like in San Francisco?")]

    model.call(messages=messages, tools=[get_current_weather])

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
                "gen_ai.tool.definitions": '[{"name":"get_current_weather","description":"Get the current weather in a given location.","strict":false,"parameters":{"properties":{"location":{"title":"Location","type":"string"},"unit":{"default":"fahrenheit","title":"Unit","type":"string"}},"required":["location"],"additionalProperties":false,"$defs":null}}]',
                "gen_ai.response.model": "openai/gpt-4o-mini",
                "gen_ai.response.finish_reasons": ["stop"],
                "gen_ai.response.id": "resp_01a49b3ee0a2578500691448c3d8b88194b5a7507bef965031",
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"What\'s the weather like in San Francisco?"}]}]',
                "gen_ai.output.messages": '[{"role":"assistant","parts":[{"type":"tool_call","id":"call_Y3kZyVbjyhkatuwQCffwwZNP","name":"get_current_weather","arguments":{"location":"San Francisco"}}],"finish_reason":"stop"}]',
            },
        }
    )


@pytest.mark.vcr()
def test_model_call_with_parameters(span_exporter: InMemorySpanExporter) -> None:
    """Test OpenTelemetry instrumentation with model parameters."""
    model_params: dict[str, Any] = {
        "temperature": 0.5,
        "max_tokens": 50,
        "top_p": 0.8,
        "frequency_penalty": 0.2,
        "presence_penalty": 0.1,
    }
    model = llm.Model(
        model_id="openai/gpt-4o-mini",
        **model_params,
    )
    messages = [llm.messages.user("Count from 1 to 5")]

    model.call(messages=messages)

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
                "gen_ai.request.temperature": 0.5,
                "gen_ai.request.max_tokens": 50,
                "gen_ai.request.top_p": 0.8,
                "gen_ai.request.frequency_penalty": 0.2,
                "gen_ai.request.presence_penalty": 0.1,
                "gen_ai.response.model": "openai/gpt-4o-mini",
                "gen_ai.response.finish_reasons": ["stop"],
                "gen_ai.response.id": "resp_040cbfa7241e8c2e00691448c521408194a985acda1297a136",
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"Count from 1 to 5"}]}]',
                "gen_ai.output.messages": '[{"role":"assistant","parts":[{"type":"text","content":"1, 2, 3, 4, 5."}],"finish_reason":"stop"}]',
            },
        }
    )


@pytest.mark.vcr()
def test_model_call_with_json_format(span_exporter: InMemorySpanExporter) -> None:
    """Test OpenTelemetry instrumentation with structured output."""
    ops.configure()

    class Person(BaseModel):
        name: str
        age: int

    ops.instrument_llm()
    model = llm.Model(model_id="openai/gpt-4o-mini")
    messages = [
        llm.messages.user("Return a person named Alice who is 30 years old as JSON")
    ]

    model.call(messages=messages, format=Person)

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
                "gen_ai.output.type": "json",
                "gen_ai.response.model": "openai/gpt-4o-mini",
                "gen_ai.response.finish_reasons": ["stop"],
                "gen_ai.response.id": "resp_034d6a18f8f9b04d00691448c897908190bc7902109227fbd1",
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"Return a person named Alice who is 30 years old as JSON"}]}]',
                "gen_ai.output.messages": '[{"role":"assistant","parts":[{"type":"text","content":"{\\"name\\":\\"Alice\\",\\"age\\":30}"}],"finish_reason":"stop"}]',
            },
        }
    )


@pytest.mark.vcr()
def test_model_call_with_image(span_exporter: InMemorySpanExporter) -> None:
    """Test OpenTelemetry instrumentation with image content."""
    model = llm.Model(model_id="openai/gpt-4o-mini")
    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
    messages = [
        llm.messages.user(
            [
                "What's in this image?",
                llm.Image.from_url(image_url),
            ]
        )
    ]

    model.call(messages=messages)

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
                "gen_ai.response.id": "resp_059298961709406100691448ca3f9c8195b58fedfa1e53ddae",
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"What\'s in this image?"},{"type":"uri","modality":"image","uri":"https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"}]}]',
                "gen_ai.output.messages": '[{"role":"assistant","parts":[{"type":"text","content":"The image depicts a serene landscape featuring a wooden pathway leading through a lush green marsh or field. The area is surrounded by tall grass and shrubs, with trees in the background. The sky above is bright with soft clouds, creating a peaceful atmosphere. This setting suggests a natural environment, ideal for walking or exploring nature."}],"finish_reason":"stop"}]',
            },
        }
    )


def test_model_call_with_error(span_exporter: InMemorySpanExporter) -> None:
    """Test OpenTelemetry instrumentation when an error occurs."""
    # Create a mock provider that raises an error
    mock_provider = Mock()
    mock_provider.id = "openai"
    mock_provider.call.side_effect = openai.APIError(
        "Server error occurred",
        request=httpx.Request("POST", "https://example.com"),
        body=None,
    )

    # Register the broken provider
    llm.register_provider(mock_provider, scope="openai/")

    model = llm.Model(model_id="openai/gpt-4o-mini")
    messages = [llm.messages.user("Hello")]

    with pytest.raises(openai.APIError):
        model.call(messages=messages)

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
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"Hello"}]}]',
                "error.type": "APIError",
                "error.message": "Server error occurred",
            },
        }
    )


@pytest.mark.vcr()
def test_model_call_records_untracked_params_event(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Ensure unsupported params are preserved via OTLP events instead of dropped."""

    class _NonSerializable:
        def __str__(self) -> str:
            return "custom-param"

    class _BadStr:
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

    model.call(messages=messages)

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


@pytest.mark.vcr()
def test_model_call_with_none_parameters(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that None parameter values are skipped in span attributes."""
    model = llm.Model(
        model_id="openai/gpt-4o-mini",
        temperature=None,  # type: ignore
        max_tokens=50,
        top_p=None,  # type: ignore
    )
    messages = [llm.messages.user("Say hello")]

    model.call(messages=messages)

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
                "gen_ai.request.max_tokens": 50,
                "gen_ai.response.model": "openai/gpt-4o-mini",
                "gen_ai.response.finish_reasons": ["stop"],
                "gen_ai.response.id": "resp_0d7415c9c4354f3d00691448d730348190949080c88fea1ed2",
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"Say hello"}]}]',
                "gen_ai.output.messages": '[{"role":"assistant","parts":[{"type":"text","content":"Hello! How can I assist you today?"}],"finish_reason":"stop"}]',
            },
        }
    )


@pytest.mark.vcr()
def test_model_call_with_base64_image(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test OpenTelemetry instrumentation with base64-encoded image content."""
    ops.instrument_llm()
    model = llm.Model(model_id="openai/gpt-4o-mini")
    # 1x1 red pixel PNG
    base64_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="
    messages = [
        llm.messages.user(
            [
                "What color is this pixel?",
                Image(
                    source=Base64ImageSource(
                        type="base64_image_source",
                        data=base64_image,
                        mime_type="image/png",
                    )
                ),
            ]
        )
    ]

    response = model.call(messages=messages)
    assert response.content

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
                "gen_ai.response.id": "resp_0f873f56169b6cf2006915837c2d6c81949f5b0dced4f89e59",
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"What color is this pixel?"},{"type":"blob","modality":"image","mime_type":"image/png","content":"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="}]}]',
                "gen_ai.output.messages": '[{"role":"assistant","parts":[{"type":"text","content":"The color of this pixel is bright red."}],"finish_reason":"stop"}]',
            },
        }
    )


def test_uninstrument_llm() -> None:
    """Test uninstrumentation and re-instrumentation is idempotent."""
    ops.uninstrument_llm()

    ops.instrument_llm()
    first_call = llm.Model.call
    ops.instrument_llm()
    assert llm.Model.call is first_call

    ops.uninstrument_llm()


@pytest.mark.vcr()
def test_model_call_with_tool_outputs(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test OpenTelemetry instrumentation with multi-turn tool conversation."""

    @llm.tool
    def get_weather(location: str) -> str:
        """Get the current weather for a location."""
        return f"Weather in {location}: 72°F, sunny"

    model = llm.Model(model_id="openai/gpt-4o-mini")
    messages = [llm.messages.user("What's the weather in Tokyo?")]
    response1 = model.call(messages=messages, tools=[get_weather])
    tool_outputs = response1.execute_tools()
    messages_with_outputs = response1.messages + [llm.messages.user(tool_outputs)]
    model.call(messages=messages_with_outputs, tools=[get_weather])

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 2
    second_span_dict = span_snapshot(spans[1])
    assert second_span_dict == snapshot(
        {
            "name": "chat openai/gpt-4o-mini",
            "kind": "CLIENT",
            "status": "UNSET",
            "attributes": {
                "gen_ai.operation.name": "chat",
                "gen_ai.provider.name": "openai",
                "gen_ai.request.model": "openai/gpt-4o-mini",
                "gen_ai.output.type": "text",
                "gen_ai.tool.definitions": '[{"name":"get_weather","description":"Get the current weather for a location.","strict":false,"parameters":{"properties":{"location":{"title":"Location","type":"string"}},"required":["location"],"additionalProperties":false,"$defs":null}}]',
                "gen_ai.response.model": "openai/gpt-4o-mini",
                "gen_ai.response.finish_reasons": ["stop"],
                "gen_ai.response.id": "resp_078dc246495066dd0069159645dfa08190b52fc7846f8b790d",
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"What\'s the weather in Tokyo?"}]},{"role":"assistant","parts":[{"type":"tool_call","id":"call_W4leLhMeS7Jo9ahswUPYo2Cd","name":"get_weather","arguments":{"location":"Tokyo"}}]},{"role":"user","parts":[{"type":"tool_call_response","id":"call_W4leLhMeS7Jo9ahswUPYo2Cd","response":"Weather in Tokyo: 72°F, sunny"}]}]',
                "gen_ai.output.messages": '[{"role":"assistant","parts":[{"type":"text","content":"The weather in Tokyo is currently sunny with a temperature of 72°F."}],"finish_reason":"stop"}]',
            },
        }
    )


@pytest.mark.vcr()
def test_model_call_with_audio_content(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test OpenTelemetry instrumentation with audio input."""
    model = llm.Model(model_id="google/gemini-2.5-flash")

    audio_path = str(
        Path(__file__).parent.parent / "e2e" / "assets" / "audio" / "tagline.mp3"
    )
    audio = Audio.from_file(audio_path)
    messages = [llm.messages.user(["What is in this audio?", audio])]

    model.call(messages=messages)

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    first_span = span_snapshot(spans[0])
    attributes = first_span["attributes"]
    assert isinstance(attributes, dict)
    input_messages_str = attributes.pop("gen_ai.input.messages")
    assert isinstance(input_messages_str, str)
    input_messages = json.loads(input_messages_str)
    # Extract base64 audio content separately to avoid codespell false positives in snapshots
    audio_content = input_messages[0]["parts"][1].pop("content")
    assert audio_content == audio.source.data
    assert json.dumps(input_messages) == snapshot(
        '[{"role": "user", "parts": [{"type": "text", "content": "What is in this audio?"}, {"type": "blob", "modality": "audio", "mime_type": "audio/mp3"}]}]'
    )

    assert first_span == snapshot(
        {
            "name": "chat google/gemini-2.5-flash",
            "kind": "CLIENT",
            "status": "UNSET",
            "attributes": {
                "gen_ai.operation.name": "chat",
                "gen_ai.provider.name": "google",
                "gen_ai.request.model": "google/gemini-2.5-flash",
                "gen_ai.output.type": "text",
                "gen_ai.response.model": "google/gemini-2.5-flash",
                "gen_ai.response.finish_reasons": ["stop"],
                "gen_ai.output.messages": '[{"role":"assistant","parts":[{"type":"text","content":"This audio contains:\\n\\n1.  A **male voice speaking** the phrase: \\"LLM abstractions that aren\'t abstractions.\\"\\n2.  Immediately following the speech, there is a distinct, **high-pitched electronic hum or whine** that lasts for about two seconds. This sound could be characteristic of coil whine, a small motor, or electronic interference."}],"finish_reason":"stop"}]',
            },
        }
    )


@pytest.mark.vcr()
def test_model_call_with_reasoning_model(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test OpenTelemetry instrumentation with reasoning model (Thought content)."""
    model = llm.Model(
        model_id="anthropic/claude-sonnet-4-20250514",
        thinking=True,
    )
    messages = [llm.messages.user("What is 2+2? Think step by step.")]

    model.call(messages=messages)

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span_dict = span_snapshot(spans[0])
    assert span_dict == snapshot(
        {
            "name": "chat anthropic/claude-sonnet-4-20250514",
            "kind": "CLIENT",
            "status": "UNSET",
            "attributes": {
                "gen_ai.operation.name": "chat",
                "gen_ai.provider.name": "anthropic",
                "gen_ai.request.model": "anthropic/claude-sonnet-4-20250514",
                "gen_ai.output.type": "text",
                "gen_ai.response.model": "anthropic/claude-sonnet-4-20250514",
                "gen_ai.response.finish_reasons": ["stop"],
                "gen_ai.response.id": "msg_015wBHMrr9GvYPVmGn1j2mmK",
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"What is 2+2? Think step by step."}]}]',
                "gen_ai.output.messages": '[{"role":"assistant","parts":[{"type":"reasoning","content":"This is a very simple arithmetic question. Let me think through it step by step as requested.\\n\\n2 + 2\\n\\nStep 1: I have the number 2\\nStep 2: I need to add another 2 to it\\nStep 3: 2 + 2 = 4\\n\\nThis is basic addition. I can think of it as:\\n- Starting with 2\\n- Adding 2 more\\n- 2, 3, 4 (counting up by 2)\\n- Or simply knowing that 2 + 2 = 4\\n\\nThe answer is 4."},{"type":"text","content":"I\'ll solve 2 + 2 step by step:\\n\\n**Step 1:** Start with the first number: 2\\n\\n**Step 2:** Add the second number: 2\\n\\n**Step 3:** Perform the addition:\\n2 + 2 = 4\\n\\n**Answer:** 4\\n\\nThis can also be thought of as counting: if you have 2 items and add 2 more items, you end up with 4 items total."}],"finish_reason":"stop"}]',
            },
        }
    )


@pytest.mark.vcr()
def test_model_call_with_stop_string(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test OpenTelemetry instrumentation with stop as a string (not list)."""
    model = llm.Model(
        model_id="openai/gpt-4o-mini:completions",
        stop="END",  # pyright: ignore [reportCallIssue]
    )
    messages = [llm.messages.user("Say hello")]

    model.call(messages=messages)

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    first_span_dict = span_snapshot(spans[0])
    assert first_span_dict == snapshot(
        {
            "name": "chat openai/gpt-4o-mini:completions",
            "kind": "CLIENT",
            "status": "UNSET",
            "attributes": {
                "gen_ai.operation.name": "chat",
                "gen_ai.provider.name": "openai",
                "gen_ai.request.model": "openai/gpt-4o-mini:completions",
                "gen_ai.output.type": "text",
                "gen_ai.request.stop_sequences": ["END"],
                "gen_ai.response.model": "openai/gpt-4o-mini:completions",
                "gen_ai.response.finish_reasons": ["stop"],
                "gen_ai.response.id": "chatcmpl-CbPJmygYNvzYcJeStNI1mOCFZRPN5",
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"Say hello"}]}]',
                "gen_ai.output.messages": '[{"role":"assistant","parts":[{"type":"text","content":"Hello! How can I assist you today?"}],"finish_reason":"stop"}]',
            },
        }
    )


@pytest.mark.vcr()
def test_model_call_without_instrumentation(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that model.call works without instrumentation (no spans created)."""
    ops.uninstrument_llm()

    model = llm.Model(model_id="openai/gpt-4o-mini")
    messages = [llm.messages.user("Hello")]

    response = model.call(messages=messages)

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

    response = model.call(messages=messages)

    assert response.content
    spans = span_exporter.get_finished_spans()
    assert len(spans) == 0


@pytest.mark.vcr()
def test_model_call_records_response_id(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that response_id is extracted and recorded in span attributes."""
    model = llm.Model(model_id="openai/gpt-4o-mini")
    messages = [llm.messages.user("Say hello")]

    response = model.call(messages=messages)

    assert hasattr(response.raw, "id")

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    first_span_dict = span_snapshot(spans[0])
    assert first_span_dict == snapshot(
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
                "gen_ai.response.id": "resp_07823e07fc5e11d7006915bf7b0e4c81949d25229918fa7c9c",
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"Say hello"}]}]',
                "gen_ai.output.messages": '[{"role":"assistant","parts":[{"type":"text","content":"Hello! How can I assist you today?"}],"finish_reason":"stop"}]',
            },
        }
    )


@pytest.mark.vcr()
def test_model_call_with_message_name(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that message name field is serialized in GenAI span attributes."""
    model = llm.Model(model_id="openai/gpt-4o-mini")

    user_msg = llm.messages.UserMessage(
        content=[Text(text="What is 1+1?")], name="calculator_user"
    )
    messages = [user_msg]

    response = model.call(messages=messages)

    assert response.content
    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    first_span_dict = span_snapshot(spans[0])
    assert first_span_dict == snapshot(
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
                "gen_ai.response.id": "resp_0727bc32da4ffb69006915caaf3f3c81969c5045f4b078be93",
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"What is 1+1?"}],"name":"calculator_user"}]',
                "gen_ai.output.messages": '[{"role":"assistant","parts":[{"type":"text","content":"1 + 1 equals 2."}],"finish_reason":"stop"}]',
            },
        }
    )


def test_model_call_with_format_tool_finish_reason(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Ensure tool-format calls capture assistant names and MAX_TOKENS finish reason."""
    book_format = llm.format(Book, mode="tool")
    assert book_format is not None

    class _FormatToolProvider:
        id: llm.ProviderId = "openai"

        def call(
            self,
            *,
            model_id: str,
            messages: Sequence[Any],
            tools: Sequence[Any] | None = None,
            format: Any = None,  # noqa: ANN401
            **params: Any,  # noqa: ANN401
        ) -> llm.Response:
            assistant_message = llm.messages.assistant(
                "Here is your book.",
                model_id=model_id,
                provider_id=self.id,
                name="assistant-1",
            )
            return llm.Response(
                raw={"responseId": "resp_format_tool_finish"},
                usage=None,
                provider_id=self.id,
                model_id=model_id,
                provider_model_name="gpt-4o-mini",
                params=params,  # pyright: ignore [reportArgumentType]
                tools=tools,
                format=format,
                input_messages=list(messages),
                assistant_message=assistant_message,
                finish_reason=FinishReason.MAX_TOKENS,
            )

    # Register the mock provider
    llm.register_provider(_FormatToolProvider(), scope="openai/")  # pyright: ignore[reportCallIssue, reportArgumentType]

    model = llm.Model(
        model_id="openai/gpt-4o-mini",
        max_tokens=5,
    )
    messages = [llm.messages.user("Return a book recommendation.")]

    response = model.call(messages=messages, format=book_format)
    assert response.finish_reason == FinishReason.MAX_TOKENS

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
                "gen_ai.output.type": "json",
                "gen_ai.request.max_tokens": 5,
                "gen_ai.tool.definitions": '[{"name":"__mirascope_formatted_output_tool__","description":"Use this tool to extract data in Book format for a final response.\\nA book with title and author.","strict":true,"parameters":{"properties":{"title":{"title":"Title","type":"string"},"author":{"title":"Author","type":"string"}},"required":["title","author"],"additionalProperties":false,"$defs":null}}]',
                "gen_ai.response.model": "openai/gpt-4o-mini",
                "gen_ai.response.finish_reasons": ["length"],
                "gen_ai.response.id": "resp_format_tool_finish",
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"Return a book recommendation."}]}]',
                "gen_ai.output.messages": '[{"role":"assistant","parts":[{"type":"text","content":"Here is your book."}],"finish_reason":"length","name":"assistant-1"}]',
            },
        }
    )


@pytest.mark.vcr()
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
        response = model.call(messages=messages)
        assert response.content

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 0
