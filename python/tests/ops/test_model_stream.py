"""OpenTelemetry integration tests for `llm.Model.stream`."""

from __future__ import annotations

from collections.abc import Generator, Iterator, Mapping
from typing import TypedDict
from unittest.mock import Mock

import httpx
import openai
import pytest
from inline_snapshot import snapshot
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)
from pydantic import BaseModel, Field

from mirascope import llm, ops
from mirascope.llm.content.text import TextChunk, TextStartChunk
from mirascope.llm.providers.provider_registry import PROVIDER_REGISTRY
from mirascope.llm.responses import StreamResponseChunk
from mirascope.llm.responses.stream_response import StreamResponse
from mirascope.ops._internal.configuration import set_tracer
from tests.ops.utils import span_snapshot


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


def _math_messages() -> list[llm.Message]:
    """Return a simple math prompt for streaming tests."""
    return [llm.messages.user("What is 4200 + 42?")]


@pytest.mark.vcr()
def test_model_stream_exports_genai_span(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that streaming a model call exports the correct OpenTelemetry span."""
    ops.instrument_llm()
    model = llm.Model(model_id="openai/gpt-4o")

    response = model.stream(messages=_math_messages())
    response.finish()

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1


@pytest.mark.vcr()
def test_model_stream_with_tools(span_exporter: InMemorySpanExporter) -> None:
    """Test that streaming a model call exports the correct OpenTelemetry span."""
    ops.instrument_llm()

    @llm.tool
    def secret_retrieval_tool(password: str) -> str:
        """A tool that requires a password to retrieve a secret."""

        return f"Retrieved secret for {password}"

    model = llm.Model(model_id="openai/gpt-4o")
    messages = [
        llm.messages.system("Use parallel tool calling."),
        llm.messages.user(
            "Please retrieve the secrets associated with each of these passwords: mellon,radiance"
        ),
    ]

    response = model.stream(messages=messages, tools=[secret_retrieval_tool])
    response.finish()

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span_dict = span_snapshot(spans[0])
    assert span_dict == snapshot(
        {
            "name": "chat openai/gpt-4o",
            "kind": "CLIENT",
            "status": "UNSET",
            "attributes": {
                "gen_ai.operation.name": "chat",
                "gen_ai.provider.name": "openai",
                "gen_ai.request.model": "openai/gpt-4o",
                "gen_ai.output.type": "text",
                "gen_ai.tool.definitions": '[{"name":"secret_retrieval_tool","description":"A tool that requires a password to retrieve a secret.","strict":false,"parameters":{"properties":{"password":{"title":"Password","type":"string"}},"required":["password"],"additionalProperties":false,"$defs":null}}]',
                "gen_ai.response.model": "openai/gpt-4o",
                "gen_ai.response.finish_reasons": ["stop"],
                "gen_ai.system_instructions": '[{"type":"text","content":"Use parallel tool calling."}]',
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"Please retrieve the secrets associated with each of these passwords: mellon,radiance"}]}]',
                "gen_ai.output.messages": '[{"role":"assistant","parts":[{"type":"tool_call","id":"call_tVwplip8EyrgMsD2ZarNBIFJ","name":"secret_retrieval_tool","arguments":{"password":"mellon"}},{"type":"tool_call","id":"call_MHKI6t2Q3p5qwBAm21ysBMIc","name":"secret_retrieval_tool","arguments":{"password":"radiance"}}],"finish_reason":"stop"}]',
            },
        }
    )


@pytest.mark.vcr()
def test_model_stream_with_json_format(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that streaming a model call exports the correct OpenTelemetry span."""

    class Author(BaseModel):
        """The author of a book."""

        first_name: str
        last_name: str

    class Book(BaseModel):
        """A book with a rating. The title should be in all caps!"""

        title: str
        author: Author
        rating: int = Field(description="For testing purposes, the rating should be 7")

    ops.instrument_llm()
    model = llm.Model(model_id="openai/gpt-4o")
    messages = [
        llm.messages.system(
            "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output."
        ),
        llm.messages.user("Please recommend the most popular book by Patrick Rothfuss"),
    ]

    response_format = llm.format(Book, mode="tool")
    response = model.stream(messages=messages, format=response_format)
    response.finish()

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span_dict = span_snapshot(spans[0])
    assert span_dict == snapshot(
        {
            "name": "chat openai/gpt-4o",
            "kind": "CLIENT",
            "status": "UNSET",
            "attributes": {
                "gen_ai.operation.name": "chat",
                "gen_ai.provider.name": "openai",
                "gen_ai.request.model": "openai/gpt-4o",
                "gen_ai.output.type": "json",
                "gen_ai.tool.definitions": '[{"name":"__mirascope_formatted_output_tool__","description":"Use this tool to extract data in Book format for a final response.\\nA book with a rating. The title should be in all caps!","strict":true,"parameters":{"properties":{"title":{"title":"Title","type":"string"},"author":{"$ref":"#/$defs/Author"},"rating":{"description":"For testing purposes, the rating should be 7","title":"Rating","type":"integer"}},"required":["title","author","rating"],"additionalProperties":false,"$defs":{"Author":{"description":"The author of a book.","properties":{"first_name":{"title":"First Name","type":"string"},"last_name":{"title":"Last Name","type":"string"}},"required":["first_name","last_name"],"title":"Author","type":"object"}}}}]',
                "gen_ai.response.model": "openai/gpt-4o",
                "gen_ai.response.finish_reasons": ["stop"],
                "gen_ai.system_instructions": '[{"type":"text","content":"Always respond to the user\'s query using the __mirascope_formatted_output_tool__ tool for structured output."}]',
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"Please recommend the most popular book by Patrick Rothfuss"}]}]',
                "gen_ai.output.messages": '[{"role":"assistant","parts":[{"type":"text","content":"{\\"title\\":\\"THE NAME OF THE WIND\\",\\"author\\":{\\"first_name\\":\\"Patrick\\",\\"last_name\\":\\"Rothfuss\\"},\\"rating\\":7}"}],"finish_reason":"stop"}]',
            },
        }
    )


@pytest.mark.vcr()
def test_model_stream_records_untracked_params_event(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that streaming a model call exports the correct OpenTelemetry span."""
    ops.instrument_llm()

    class _NonSerializable:
        """Dummy object that stringifies cleanly for untracked params tests."""

        def __str__(self) -> str:
            return "custom-param"

    class _BadStr:
        """Dummy object whose __str__ intentionally raises."""

        def __str__(self) -> str:  # pragma: no cover - forced failure path
            raise ValueError("cannot stringify")

    class _TraceMetadata(TypedDict):
        """Trace metadata payload."""

        id: str
        tags: list[str]

    class _Metadata(TypedDict):
        """Metadata container for trace info."""

        trace: _TraceMetadata

    class _ExtraParams(llm.Params, total=False):
        """Params with unsupported and serializable extras for testing."""

        metadata: _Metadata
        unsupported_list: list[int]
        non_serializable: _NonSerializable
        bad_str: _BadStr

    extra_params: _ExtraParams = {
        "metadata": {"trace": {"id": "abc123", "tags": ["otel"]}},
        "unsupported_list": [1, 2, 3],
        "non_serializable": _NonSerializable(),
        "bad_str": _BadStr(),
    }
    model = llm.Model(
        model_id="openai/gpt-4o",
        **extra_params,
    )

    response = model.stream(messages=_math_messages())
    response.finish()

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    events = spans[0].events
    event = events[-1]
    event_attributes: Mapping[str, object] = event.attributes or {}
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
def test_model_stream_with_none_parameters(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that streaming a model call exports the correct OpenTelemetry span."""
    ops.instrument_llm()
    model = llm.Model(
        model_id="openai/gpt-4o",
        temperature=None,  # type: ignore[arg-type]
        max_tokens=64,
        top_p=None,  # type: ignore[arg-type]
    )

    response = model.stream(messages=_math_messages())
    response.finish()

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span_dict = span_snapshot(spans[0])
    assert span_dict == snapshot(
        {
            "name": "chat openai/gpt-4o",
            "kind": "CLIENT",
            "status": "UNSET",
            "attributes": {
                "gen_ai.operation.name": "chat",
                "gen_ai.provider.name": "openai",
                "gen_ai.request.model": "openai/gpt-4o",
                "gen_ai.output.type": "text",
                "gen_ai.request.max_tokens": 64,
                "gen_ai.response.model": "openai/gpt-4o",
                "gen_ai.response.finish_reasons": ["stop"],
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"What is 4200 + 42?"}]}]',
                "gen_ai.output.messages": '[{"role":"assistant","parts":[{"type":"text","content":"4200 + 42 = 4242"}],"finish_reason":"stop"}]',
            },
        }
    )


@pytest.mark.vcr()
def test_model_stream_records_response_id(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that streaming a model call exports the correct OpenTelemetry span."""
    ops.instrument_llm()
    model = llm.Model(model_id="openai/gpt-4o")

    response = model.stream(messages=_math_messages())
    response.finish()

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    attrs = spans[0].attributes or {}
    assert "gen_ai.response.id" not in attrs
    first_span_dict = span_snapshot(spans[0])
    assert first_span_dict == snapshot(
        {
            "name": "chat openai/gpt-4o",
            "kind": "CLIENT",
            "status": "UNSET",
            "attributes": {
                "gen_ai.operation.name": "chat",
                "gen_ai.provider.name": "openai",
                "gen_ai.request.model": "openai/gpt-4o",
                "gen_ai.output.type": "text",
                "gen_ai.response.model": "openai/gpt-4o",
                "gen_ai.response.finish_reasons": ["stop"],
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"What is 4200 + 42?"}]}]',
                "gen_ai.output.messages": '[{"role":"assistant","parts":[{"type":"text","content":"4200 + 42 equals 4242."}],"finish_reason":"stop"}]',
            },
        }
    )


@pytest.mark.vcr()
def test_model_stream_without_instrumentation(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that streaming a model call exports the correct OpenTelemetry span."""
    ops.uninstrument_llm()

    model = llm.Model(model_id="openai/gpt-4o")
    response = model.stream(messages=_math_messages())
    response.finish()

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 0


@pytest.mark.vcr()
def test_model_stream_with_tracer_set_to_none(
    span_exporter: InMemorySpanExporter,
) -> None:
    ops.instrument_llm()
    set_tracer(None)

    model = llm.Model(model_id="openai/gpt-4o")
    response = model.stream(messages=_math_messages())
    response.finish()

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 0


def test_model_stream_with_error(span_exporter: InMemorySpanExporter) -> None:
    """Test that streaming a model call exports the correct OpenTelemetry span."""
    ops.instrument_llm()

    # Create a mock provider that raises an error
    mock_provider = Mock()
    mock_provider.id = "openai"
    mock_provider.stream.side_effect = openai.APIError(
        "Server error occurred",
        request=httpx.Request("POST", "https://example.com"),
        body=None,
    )

    # Register the broken provider
    llm.register_provider(mock_provider, scope="openai/")

    model = llm.Model(model_id="openai/gpt-4o")
    with pytest.raises(openai.APIError):
        model.stream(messages=_math_messages())

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span_dict = span_snapshot(spans[0])
    assert span_dict == snapshot(
        {
            "name": "chat openai/gpt-4o",
            "kind": "CLIENT",
            "status": "ERROR",
            "attributes": {
                "gen_ai.operation.name": "chat",
                "gen_ai.provider.name": "openai",
                "gen_ai.request.model": "openai/gpt-4o",
                "gen_ai.output.type": "text",
                "gen_ai.input.messages": '[{"role":"user","parts":[{"type":"text","content":"What is 4200 + 42?"}]}]',
                "error.type": "APIError",
                "error.message": "Server error occurred",
            },
        }
    )


def test_model_stream_iterator_error_records_exception(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that streaming a model call exports the correct OpenTelemetry span."""
    ops.instrument_llm()

    def _chunk_iterator() -> Iterator[StreamResponseChunk]:
        """Return a chunk iterator that raises to simulate stream failure."""
        yield TextStartChunk()
        yield TextChunk(delta="partial")
        raise RuntimeError("chunk boom")

    # Create a mock provider that returns a failing stream
    mock_provider = Mock()
    mock_provider.id = "openai"
    mock_provider.stream.return_value = StreamResponse(
        provider_id="openai",
        model_id="openai/gpt-4o",
        provider_model_name="gpt-4o:responses",
        params={},
        tools=None,
        format=None,
        input_messages=_math_messages(),
        chunk_iterator=_chunk_iterator(),
    )

    # Register the mock provider
    llm.register_provider(mock_provider, scope="openai/")

    model = llm.Model(model_id="openai/gpt-4o")
    response = model.stream(messages=_math_messages())
    with pytest.raises(RuntimeError):
        response.finish()

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]
    assert span.status.status_code.name == "ERROR"
    attrs = span.attributes or {}
    assert attrs["error.type"] == "RuntimeError"
    assert attrs["error.message"] == "chunk boom"
