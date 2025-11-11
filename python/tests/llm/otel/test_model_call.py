"""OpenTelemetry integration test for `llm.Model.call`."""

from __future__ import annotations

import json
from collections.abc import Generator, Mapping, Sequence
from typing import Any, TypedDict, cast
from unittest.mock import Mock, patch

import httpx
import openai
import opentelemetry.trace as otel_trace
import pytest
from inline_snapshot import snapshot
from opentelemetry import trace
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)
from pydantic import BaseModel

from mirascope import llm
from mirascope.llm.content import (
    Audio,
    Base64AudioSource,
    Base64DocumentSource,
    Base64ImageSource,
    Document,
    Image,
    Text,
    TextDocumentSource,
    Thought,
    ToolCall,
    ToolOutput,
    URLDocumentSource,
)
from mirascope.llm.formatting import Format
from mirascope.llm.messages import AssistantMessage, UserMessage
from mirascope.llm.otel import _span
from mirascope.llm.otel._messages import serialize_response_messages
from mirascope.llm.responses.finish_reason import FinishReason


@pytest.fixture(scope="session")
def vcr_config() -> dict[str, object]:
    return {
        "record_mode": "once",
        "match_on": ["method", "uri", "body"],
        "filter_headers": ["authorization", "cookie"],
        "filter_post_data_parameters": [],
    }


@pytest.fixture()
def span_exporter() -> Generator[InMemorySpanExporter, None, None]:
    provider = TracerProvider()
    exporter = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    otel_trace._TRACER_PROVIDER = None
    once_ctor = otel_trace.Once  # type: ignore
    otel_trace._TRACER_PROVIDER_SET_ONCE = once_ctor()
    trace.set_tracer_provider(provider)
    exporter.clear()
    yield exporter
    exporter.clear()
    llm.uninstrument_opentelemetry()
    otel_trace._TRACER_PROVIDER = None
    otel_trace._TRACER_PROVIDER_SET_ONCE = once_ctor()


class SpanSnapshot(TypedDict):
    name: str
    kind: str
    status: str
    attributes: Mapping[str, object]


def _span_snapshot(span: ReadableSpan) -> SpanSnapshot:
    attrs = span.attributes or {}
    serializable_attrs: dict[str, object] = {
        key: list(value) if isinstance(value, tuple) else value
        for key, value in attrs.items()
    }
    return {
        "name": span.name,
        "kind": span.kind.name,
        "status": span.status.status_code.name,
        "attributes": serializable_attrs,
    }


class _DummyResponse:
    def __init__(
        self,
        *,
        messages: Sequence[Any],
        finish_reason: FinishReason | None,
    ) -> None:
        self.messages = list(messages)
        self.finish_reason = finish_reason


@pytest.mark.vcr()
def test_model_call_exports_genai_span(span_exporter: InMemorySpanExporter) -> None:
    llm.instrument_opentelemetry(tracer_provider=trace.get_tracer_provider())
    model = llm.Model(provider="openai:responses", model_id="gpt-4o-mini")
    messages = [
        llm.messages.system("You are a concise assistant."),
        llm.messages.user("Say hello to the user named Kai."),
    ]

    response = model.call(messages=messages)
    assert "Kai" in response.pretty()

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span_dict = _span_snapshot(spans[0])
    assert span_dict == snapshot(
        {
            "name": "chat gpt-4o-mini",
            "kind": "CLIENT",
            "status": "UNSET",
            "attributes": {
                "gen_ai.operation.name": "chat",
                "gen_ai.provider.name": "openai:responses",
                "gen_ai.request.model": "gpt-4o-mini",
                "gen_ai.output.type": "text",
                "gen_ai.system_instructions": '[{"role": "system", "parts": [{"type": "text", "content": "You are a concise assistant."}]}]',
                "gen_ai.input.messages": '[{"role": "user", "parts": [{"type": "text", "content": "Say hello to the user named Kai."}]}]',
                "gen_ai.response.model": "gpt-4o-mini",
                "gen_ai.response.finish_reasons": ["stop"],
                "gen_ai.output.messages": '[{"role": "assistant", "parts": [{"type": "text", "content": "Hello, Kai!"}], "finish_reason": "stop"}]',
            },
        }
    )


@pytest.mark.vcr()
def test_model_call_with_tools(span_exporter: InMemorySpanExporter) -> None:
    """Test OpenTelemetry instrumentation with tool calling."""
    llm.instrument_opentelemetry(tracer_provider=trace.get_tracer_provider())

    @llm.tool
    def get_current_weather(location: str, unit: str = "fahrenheit") -> str:
        """Get the current weather in a given location."""
        return f"Weather in {location}: 72°{unit[0].upper()}, sunny"

    model = llm.Model(provider="openai:responses", model_id="gpt-4o-mini")
    messages = [llm.messages.user("What's the weather like in San Francisco?")]

    model.call(messages=messages, tools=[get_current_weather])

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span_dict = _span_snapshot(spans[0])
    assert span_dict == snapshot(
        {
            "name": "chat gpt-4o-mini",
            "kind": "CLIENT",
            "status": "UNSET",
            "attributes": {
                "gen_ai.operation.name": "chat",
                "gen_ai.provider.name": "openai:responses",
                "gen_ai.request.model": "gpt-4o-mini",
                "gen_ai.output.type": "text",
                "gen_ai.tool.definitions": snapshot(
                    '[{"name": "get_current_weather", "description": "Get the current weather in a given location.", "strict": false, "parameters": {"properties": {"location": {"title": "Location", "type": "string"}, "unit": {"default": "fahrenheit", "title": "Unit", "type": "string"}}, "required": ["location"], "additionalProperties": false, "$defs": null}}]'
                ),
                "gen_ai.input.messages": snapshot(
                    '[{"role": "user", "parts": [{"type": "text", "content": "What\'s the weather like in San Francisco?"}]}]'
                ),
                "gen_ai.response.model": "gpt-4o-mini",
                "gen_ai.response.finish_reasons": snapshot(["stop"]),
                "gen_ai.output.messages": snapshot(
                    '[{"role": "assistant", "parts": [{"type": "tool_call", "id": "call_Y3kZyVbjyhkatuwQCffwwZNP", "name": "get_current_weather", "arguments": {"location": "San Francisco"}}], "finish_reason": "stop"}]'
                ),
            },
        }
    )


@pytest.mark.vcr()
def test_model_call_with_parameters(span_exporter: InMemorySpanExporter) -> None:
    """Test OpenTelemetry instrumentation with model parameters."""
    llm.instrument_opentelemetry(tracer_provider=trace.get_tracer_provider())
    model_params: dict[str, Any] = {
        "temperature": 0.5,
        "max_tokens": 50,
        "top_p": 0.8,
        "frequency_penalty": 0.2,
        "presence_penalty": 0.1,
    }
    model = llm.Model(
        provider="openai:responses",
        model_id="gpt-4o-mini",
        **model_params,
    )
    messages = [llm.messages.user("Count from 1 to 5")]

    model.call(messages=messages)

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span_dict = _span_snapshot(spans[0])
    assert span_dict == snapshot(
        {
            "name": "chat gpt-4o-mini",
            "kind": "CLIENT",
            "status": "UNSET",
            "attributes": {
                "gen_ai.operation.name": "chat",
                "gen_ai.provider.name": "openai:responses",
                "gen_ai.request.model": "gpt-4o-mini",
                "gen_ai.output.type": "text",
                "gen_ai.request.temperature": 0.5,
                "gen_ai.request.max_tokens": 50,
                "gen_ai.request.top_p": 0.8,
                "gen_ai.request.frequency_penalty": 0.2,
                "gen_ai.request.presence_penalty": 0.1,
                "gen_ai.input.messages": snapshot(
                    '[{"role": "user", "parts": [{"type": "text", "content": "Count from 1 to 5"}]}]'
                ),
                "gen_ai.response.model": "gpt-4o-mini",
                "gen_ai.response.finish_reasons": snapshot(["stop"]),
                "gen_ai.output.messages": snapshot(
                    '[{"role": "assistant", "parts": [{"type": "text", "content": "1, 2, 3, 4, 5."}], "finish_reason": "stop"}]'
                ),
            },
        }
    )


@pytest.mark.vcr()
def test_model_call_with_json_format(span_exporter: InMemorySpanExporter) -> None:
    """Test OpenTelemetry instrumentation with structured output."""

    class Person(BaseModel):
        name: str
        age: int

    llm.instrument_opentelemetry(tracer_provider=trace.get_tracer_provider())
    model = llm.Model(provider="openai:responses", model_id="gpt-4o-mini")
    messages = [
        llm.messages.user("Return a person named Alice who is 30 years old as JSON")
    ]

    model.call(messages=messages, format=Person)

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span_dict = _span_snapshot(spans[0])
    assert span_dict == snapshot(
        {
            "name": "chat gpt-4o-mini",
            "kind": "CLIENT",
            "status": "UNSET",
            "attributes": {
                "gen_ai.operation.name": "chat",
                "gen_ai.provider.name": "openai:responses",
                "gen_ai.request.model": "gpt-4o-mini",
                "gen_ai.output.type": "json",
                "gen_ai.input.messages": snapshot(
                    '[{"role": "user", "parts": [{"type": "text", "content": "Return a person named Alice who is 30 years old as JSON"}]}]'
                ),
                "gen_ai.response.model": "gpt-4o-mini",
                "gen_ai.response.finish_reasons": snapshot(["stop"]),
                "gen_ai.output.messages": snapshot(
                    '[{"role": "assistant", "parts": [{"type": "text", "content": "{\\"name\\":\\"Alice\\",\\"age\\":30}"}], "finish_reason": "stop"}]'
                ),
            },
        }
    )


@pytest.mark.vcr()
def test_model_call_with_image(span_exporter: InMemorySpanExporter) -> None:
    """Test OpenTelemetry instrumentation with image content."""
    llm.instrument_opentelemetry(tracer_provider=trace.get_tracer_provider())
    model = llm.Model(provider="openai:responses", model_id="gpt-4o-mini")
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
    span_dict = _span_snapshot(spans[0])
    assert span_dict == snapshot(
        {
            "name": "chat gpt-4o-mini",
            "kind": "CLIENT",
            "status": "UNSET",
            "attributes": {
                "gen_ai.operation.name": "chat",
                "gen_ai.provider.name": "openai:responses",
                "gen_ai.request.model": "gpt-4o-mini",
                "gen_ai.output.type": "text",
                "gen_ai.input.messages": snapshot(
                    '[{"role": "user", "parts": [{"type": "text", "content": "What\'s in this image?"}, {"type": "uri", "modality": "image", "uri": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"}]}]'
                ),
                "gen_ai.response.model": "gpt-4o-mini",
                "gen_ai.response.finish_reasons": snapshot(["stop"]),
                "gen_ai.output.messages": snapshot(
                    '[{"role": "assistant", "parts": [{"type": "text", "content": "The image depicts a serene landscape featuring a wooden pathway leading through a lush green marsh or field. The area is surrounded by tall grass and shrubs, with trees in the background. The sky above is bright with soft clouds, creating a peaceful atmosphere. This setting suggests a natural environment, ideal for walking or exploring nature."}], "finish_reason": "stop"}]'
                ),
            },
        }
    )


def test_model_call_with_error(span_exporter: InMemorySpanExporter) -> None:
    """Test OpenTelemetry instrumentation when an error occurs."""
    llm.instrument_opentelemetry(tracer_provider=trace.get_tracer_provider())

    mock_client = Mock()
    mock_client.call.side_effect = openai.APIError(
        "Server error occurred",
        request=httpx.Request("POST", "https://example.com"),
        body=None,
    )

    with patch("mirascope.llm.models.models.get_client", return_value=mock_client):
        model = llm.Model(provider="openai:responses", model_id="gpt-4o-mini")
        messages = [llm.messages.user("Hello")]

        with pytest.raises(openai.APIError):
            model.call(messages=messages)

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span_dict = _span_snapshot(spans[0])
    assert span_dict == snapshot(
        {
            "name": "chat gpt-4o-mini",
            "kind": "CLIENT",
            "status": "ERROR",
            "attributes": {
                "gen_ai.operation.name": "chat",
                "gen_ai.provider.name": "openai:responses",
                "gen_ai.request.model": "gpt-4o-mini",
                "gen_ai.output.type": "text",
                "gen_ai.input.messages": '[{"role": "user", "parts": [{"type": "text", "content": "Hello"}]}]',
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
    llm.instrument_opentelemetry(tracer_provider=trace.get_tracer_provider())

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
        provider="openai:responses",
        model_id="gpt-4o-mini",
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
            "attributes": snapshot(
                {
                    "gen_ai.untracked_params.count": 4,
                    "gen_ai.untracked_params.keys": [
                        "metadata",
                        "unsupported_list",
                        "non_serializable",
                        "bad_str",
                    ],
                    "gen_ai.untracked_params.json": snapshot(
                        '{"metadata": "{\'trace\': {\'id\': \'abc123\', \'tags\': [\'otel\']}}", "unsupported_list": "[1, 2, 3]", "non_serializable": "custom-param", "bad_str": "<_BadStr>"}'
                    ),
                }
            ),
        }
    )


@pytest.mark.vcr()
def test_span_without_tracer_returns_none() -> None:
    llm.uninstrument_opentelemetry()
    messages = [llm.messages.user("Is tracing enabled?")]

    with _span.span(
        operation="chat",
        provider="openai:responses",
        model_id="dummy",
        messages=messages,
        tools=None,
        format=None,
        params={},
    ) as captured_span:
        assert captured_span == snapshot(None)

    _span.assign_attributes(None, {"diagnostic": "noop"})
    _span.record_exception(None, RuntimeError("span unavailable"))


@pytest.mark.vcr()
def test_span_records_exception_attributes() -> None:
    provider = TracerProvider()
    exporter = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    _span.set_tracer(provider.get_tracer("mirascope.tests"))

    messages = [llm.messages.user("Trigger a failure.")]
    try:
        with _span.span(
            operation="chat",
            provider="openai:responses",
            model_id="demo",
            messages=messages,
            tools=None,
            format=None,
            params={},
        ):
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    finally:
        _span.set_tracer(None)

    finished_spans = exporter.get_finished_spans()
    assert len(finished_spans) == 1
    span_attributes = cast(Mapping[str, object], finished_spans[0].attributes or {})
    error_snapshot = {
        "name": finished_spans[0].name,
        "status": finished_spans[0].status.status_code.name,
        "attributes": {
            key: list(value) if isinstance(value, tuple) else value
            for key, value in span_attributes.items()
        },
    }
    assert error_snapshot == snapshot(
        {
            "name": "chat demo",
            "status": "ERROR",
            "attributes": snapshot(
                {
                    "gen_ai.operation.name": "chat",
                    "gen_ai.provider.name": "openai:responses",
                    "gen_ai.request.model": "demo",
                    "gen_ai.output.type": "text",
                    "gen_ai.input.messages": snapshot(
                        '[{"role": "user", "parts": [{"type": "text", "content": "Trigger a failure."}]}]'
                    ),
                    "error.type": "RuntimeError",
                    "error.message": "boom",
                }
            ),
        }
    )


@pytest.mark.vcr()
def test_attach_response_extracts_response_id() -> None:
    user_message = UserMessage(
        role="user",
        content=[Text(text="Share status")],
        name=None,
    )
    assistant_message = AssistantMessage(
        role="assistant",
        content=[Text(text="Status ready")],
        provider="openai:responses",
        model_id="gpt-4o-mini",
        raw_message={"responseId": "resp_unit"},
        name="scribe",
    )

    class _FakeResponse:
        def __init__(
            self,
            *,
            messages: Sequence[Any],
            finish_reason: FinishReason | None,
            model_id: str,
            raw: Mapping[str, object],
        ) -> None:
            self.messages = list(messages)
            self.finish_reason = finish_reason
            self.model_id = model_id
            self.raw = raw

    response = _FakeResponse(
        messages=[user_message, assistant_message],
        finish_reason=FinishReason.MAX_TOKENS,
        model_id="gpt-4o-mini",
        raw={
            "responseId": "resp_unit",
            "usage": {"input_tokens": 42, "output_tokens": 11},
        },
    )

    class _SpanRecorder:
        def __init__(self) -> None:
            self.attributes: dict[str, object] = {}

        def set_attribute(self, key: str, value: object) -> None:
            self.attributes[key] = value

    span_recorder = _SpanRecorder()
    _span.attach_response(
        cast(Any, span_recorder), cast(Any, response), request_messages=[user_message]
    )

    assert span_recorder.attributes == snapshot(
        {
            "gen_ai.response.model": "gpt-4o-mini",
            "gen_ai.response.finish_reasons": ["length"],
            "gen_ai.response.id": "resp_unit",
            "gen_ai.output.messages": snapshot(
                '[{"role": "assistant", "parts": [{"type": "text", "content": "Status ready"}], "name": "scribe", "finish_reason": "length"}]'
            ),
            "gen_ai.input.messages": snapshot(
                '[{"role": "user", "parts": [{"type": "text", "content": "Share status"}]}]'
            ),
        }
    )


@pytest.mark.vcr()
def test_serialize_response_messages_empty() -> None:
    response = _DummyResponse(messages=[], finish_reason=None)
    assert serialize_response_messages(cast(Any, response)) == snapshot({})


@pytest.mark.vcr()
def test_apply_param_attributes_with_stop_string() -> None:
    attrs: dict[str, object] = {}
    _span.apply_param_attributes(
        cast(dict[str, _span.AttributeValue], attrs),
        cast(_span.ParamsDict, {"stop": "DONE"}),
    )
    assert attrs == snapshot({"gen_ai.request.stop_sequences": ["DONE"]})


@pytest.mark.vcr()
def test_infer_output_type_for_format_object() -> None:
    class DemoModel(BaseModel):
        value: str

    format_obj = Format(
        name="demo",
        description=None,
        schema={"type": "object"},
        mode="tool",
        formatting_instructions=None,
        formattable=DemoModel,
    )
    assert _span.infer_output_type(cast(_span.FormatParam, format_obj)) == snapshot(
        "json"
    )


@pytest.mark.vcr()
def test_serialize_tool_definitions_empty_sequence() -> None:
    assert _span.serialize_tool_definitions([]) == snapshot(None)


@pytest.mark.vcr()
def test_serialize_tool_definitions_include_format_tool() -> None:
    class Report(BaseModel):
        summary: str

    format_spec = llm.format(Report, mode="tool")
    payload = _span.serialize_tool_definitions([], cast(Format[None], format_spec))
    assert payload is not None
    assert json.loads(payload) == snapshot(
        [
            {
                "name": "__mirascope_formatted_output_tool__",
                "description": snapshot(
                    "Use this tool to extract data in Report format for a final response."
                ),
                "strict": True,
                "parameters": snapshot(
                    {
                        "properties": {
                            "summary": {
                                "title": "Summary",
                                "type": "string",
                            }
                        },
                        "required": ["summary"],
                        "additionalProperties": False,
                        "$defs": None,
                    }
                ),
            }
        ]
    )


@pytest.mark.vcr()
def test_serialize_response_messages_multimodal() -> None:
    """Serialize diverse content parts into OTEL-ready payloads."""

    class _DummySource:
        def __init__(self, label: str) -> None:
            self.label = label

        def __str__(self) -> str:
            return self.label

    system_message = llm.messages.system("Stay helpful.")
    user_message = llm.messages.user(
        [
            "Please summarize the attached artifacts.",
            Image(
                source=Base64ImageSource(
                    type="base64_image_source", data="aGVsbG8=", mime_type="image/png"
                )
            ),
            Image.from_url("https://example.com/diagram.png"),
            Image(source=cast(Any, _DummySource("sketch://fallback"))),
            Audio(
                source=Base64AudioSource(
                    type="base64_audio_source", data="UklGRg==", mime_type="audio/wav"
                )
            ),
            Audio(source=cast(Any, _DummySource("pcm://raw"))),
            Document(
                source=URLDocumentSource(
                    type="url_document_source", url="https://example.com/manual.pdf"
                )
            ),
            Document(
                source=Base64DocumentSource(
                    type="base64_document_source",
                    data="JVBERi0=",
                    media_type="application/pdf",
                )
            ),
            Document(
                source=TextDocumentSource(
                    type="text_document_source",
                    data='{"title":"Spec"}',
                    media_type="application/json",
                )
            ),
            Document(source=cast(Any, _DummySource("memory://doc"))),
            ToolOutput(id="call_weather", name="get_weather", value={"temp": 72}),
        ],
        name="kai",
    )
    assistant_message = llm.messages.assistant(
        [
            Text(text="Here is the summary:"),
            ToolCall(
                id="call_weather",
                name="get_weather",
                args='{"location":"San Francisco"}',
            ),
            ToolCall(id="call_invalid", name="debug", args="not-json"),
            Thought(thought="Ensured tools were called before responding."),
        ],
        provider="openai:responses",
        model_id="gpt-4o-mini",
        name="scout",
    )

    response = _DummyResponse(
        messages=[system_message, user_message, assistant_message],
        finish_reason=FinishReason.REFUSAL,
    )

    payload = serialize_response_messages(cast(Any, response))
    decoded = {key: json.loads(value) for key, value in payload.items()}

    assert decoded == snapshot(
        {
            "gen_ai.input.messages": snapshot(
                [
                    {
                        "name": "kai",
                        "parts": snapshot(
                            [
                                {
                                    "content": "Please summarize the attached artifacts.",
                                    "type": "text",
                                },
                                {
                                    "content": "aGVsbG8=",
                                    "mime_type": "image/png",
                                    "modality": "image",
                                    "type": "blob",
                                },
                                {
                                    "modality": "image",
                                    "type": "uri",
                                    "uri": "https://example.com/diagram.png",
                                },
                                {"source": "sketch://fallback", "type": "image"},
                                {
                                    "content": "UklGRg==",
                                    "mime_type": "audio/wav",
                                    "modality": "audio",
                                    "type": "blob",
                                },
                                {"source": "pcm://raw", "type": "audio"},
                                {
                                    "modality": "document",
                                    "type": "uri",
                                    "uri": "https://example.com/manual.pdf",
                                },
                                {
                                    "content": "JVBERi0=",
                                    "mime_type": "application/pdf",
                                    "modality": "document",
                                    "type": "blob",
                                },
                                {
                                    "content": '{"title":"Spec"}',
                                    "mime_type": "application/json",
                                    "type": "text",
                                },
                                {
                                    "modality": "document",
                                    "source": "memory://doc",
                                    "type": "generic",
                                },
                                {
                                    "id": "call_weather",
                                    "name": "get_weather",
                                    "response": {"temp": 72},
                                    "type": "tool_call_response",
                                },
                            ]
                        ),
                        "role": "user",
                    }
                ]
            ),
            "gen_ai.output.messages": snapshot(
                [
                    {
                        "finish_reason": "content_filter",
                        "name": "scout",
                        "parts": snapshot(
                            [
                                {"content": "Here is the summary:", "type": "text"},
                                {
                                    "arguments": {"location": "San Francisco"},
                                    "id": "call_weather",
                                    "name": "get_weather",
                                    "type": "tool_call",
                                },
                                {
                                    "arguments": "not-json",
                                    "id": "call_invalid",
                                    "name": "debug",
                                    "type": "tool_call",
                                },
                                {
                                    "content": "Ensured tools were called before responding.",
                                    "type": "reasoning",
                                },
                            ]
                        ),
                        "role": "assistant",
                    }
                ]
            ),
            "gen_ai.system_instructions": snapshot(
                [
                    {
                        "parts": [{"content": "Stay helpful.", "type": "text"}],
                        "role": "system",
                    }
                ]
            ),
        }
    )


@pytest.mark.vcr()
def test_model_call_with_none_parameters(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that None parameter values are skipped in span attributes."""
    llm.instrument_opentelemetry(tracer_provider=trace.get_tracer_provider())
    model = llm.Model(
        provider="openai:responses",
        model_id="gpt-4o-mini",
        temperature=None,  # type: ignore
        max_tokens=50,
        top_p=None,  # type: ignore
    )
    messages = [llm.messages.user("Say hello")]

    model.call(messages=messages)

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span_dict = _span_snapshot(spans[0])
    assert span_dict == snapshot(
        {
            "name": "chat gpt-4o-mini",
            "kind": "CLIENT",
            "status": "UNSET",
            "attributes": {
                "gen_ai.operation.name": "chat",
                "gen_ai.provider.name": "openai:responses",
                "gen_ai.request.model": "gpt-4o-mini",
                "gen_ai.output.type": "text",
                "gen_ai.request.max_tokens": 50,
                "gen_ai.input.messages": snapshot(
                    '[{"role": "user", "parts": [{"type": "text", "content": "Say hello"}]}]'
                ),
                "gen_ai.response.model": "gpt-4o-mini",
                "gen_ai.response.finish_reasons": snapshot(["stop"]),
                "gen_ai.output.messages": snapshot(
                    '[{"role": "assistant", "parts": [{"type": "text", "content": "Hello! How can I assist you today?"}], "finish_reason": "stop"}]'
                ),
            },
        }
    )


def test_uninstrument_and_is_instrumented() -> None:
    """Test uninstrumentation and checking instrumentation status."""
    llm.uninstrument_opentelemetry()
    assert not llm.is_instrumented()

    provider = TracerProvider()
    trace.set_tracer_provider(provider)
    llm.instrument_opentelemetry(tracer_provider=provider)
    assert llm.is_instrumented()
    first_call = llm.Model.call
    llm.instrument_opentelemetry(tracer_provider=provider)
    assert llm.Model.call is first_call

    llm.uninstrument_opentelemetry()
    assert not llm.is_instrumented()
