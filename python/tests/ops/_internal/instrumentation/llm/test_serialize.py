"""Unit tests for Mirascope-specific span attribute serialization."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from inline_snapshot import snapshot

from mirascope.llm.content import (
    Audio,
    Document,
    Image,
    Text,
    Thought,
    ToolCall,
    ToolOutput,
)
from mirascope.llm.content.audio import Base64AudioSource
from mirascope.llm.content.document import (
    Base64DocumentSource,
    TextDocumentSource,
    URLDocumentSource,
)
from mirascope.llm.content.image import Base64ImageSource, URLImageSource
from mirascope.llm.messages import AssistantMessage, SystemMessage, UserMessage
from mirascope.llm.responses.usage import Usage
from mirascope.llm.tools import ProviderTool
from mirascope.ops._internal.instrumentation.llm.serialize import (
    attach_mirascope_response,
    attach_mirascope_response_async,
    serialize_mirascope_content,
    serialize_mirascope_cost,
    serialize_mirascope_messages,
    serialize_mirascope_usage,
    serialize_tools,
)

if TYPE_CHECKING:
    from opentelemetry.util.types import AttributeValue


class TestSerializeContent:
    """Tests for serialize_mirascope_content function."""

    def test_serialize_text_content(self) -> None:
        """Test serialization of Text content."""
        content = [Text(text="Hello, world!")]
        result = json.loads(serialize_mirascope_content(content))
        assert result == [{"type": "text", "text": "Hello, world!"}]

    def test_serialize_tool_call_content(self) -> None:
        """Test serialization of ToolCall content."""
        content = [
            ToolCall(
                id="call_123",
                name="get_weather",
                args='{"location": "Tokyo"}',
            )
        ]
        result = json.loads(serialize_mirascope_content(content))
        assert result == [
            {
                "type": "tool_call",
                "id": "call_123",
                "name": "get_weather",
                "args": '{"location": "Tokyo"}',
            }
        ]

    def test_serialize_thought_content(self) -> None:
        """Test serialization of Thought content."""
        content = [Thought(thought="Let me think about this...")]
        result = json.loads(serialize_mirascope_content(content))
        assert result == [{"type": "thought", "thought": "Let me think about this..."}]

    def test_serialize_mixed_content(self) -> None:
        """Test serialization of mixed content types."""
        content = [
            Thought(thought="Thinking..."),
            Text(text="Here is my answer."),
            ToolCall(id="call_456", name="calculate", args='{"x": 1}'),
        ]
        result = json.loads(serialize_mirascope_content(content))
        assert len(result) == 3
        assert result[0]["type"] == "thought"
        assert result[1]["type"] == "text"
        assert result[2]["type"] == "tool_call"


class TestSerializeMessages:
    """Tests for serialize_mirascope_messages function."""

    def test_serialize_system_message(self) -> None:
        """Test serialization of SystemMessage."""
        messages = [SystemMessage(content=Text(text="You are a helpful assistant."))]
        result = json.loads(serialize_mirascope_messages(messages))
        assert result == [
            {
                "role": "system",
                "content": {"type": "text", "text": "You are a helpful assistant."},
            }
        ]

    def test_serialize_user_message(self) -> None:
        """Test serialization of UserMessage."""
        messages = [UserMessage(content=[Text(text="Hello")], name=None)]
        result = json.loads(serialize_mirascope_messages(messages))
        assert result == [
            {
                "role": "user",
                "content": [{"type": "text", "text": "Hello"}],
                "name": None,
            }
        ]

    def test_serialize_user_message_with_name(self) -> None:
        """Test serialization of UserMessage with name."""
        messages = [UserMessage(content=[Text(text="Hi")], name="alice")]
        result = json.loads(serialize_mirascope_messages(messages))
        assert result[0]["name"] == "alice"

    def test_serialize_assistant_message(self) -> None:
        """Test serialization of AssistantMessage."""
        messages = [
            AssistantMessage(
                content=[Text(text="Hello!")],
                name=None,
                provider_id="openai",
                model_id="openai/gpt-4o-mini",
                provider_model_name=None,
                raw_message=None,
            )
        ]
        result = json.loads(serialize_mirascope_messages(messages))
        assert result == [
            {
                "role": "assistant",
                "content": [{"type": "text", "text": "Hello!"}],
                "name": None,
            }
        ]

    def test_serialize_tool_output_in_user_message(self) -> None:
        """Test serialization of ToolOutput in UserMessage."""
        messages = [
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_123",
                        name="get_weather",
                        result="72°F, sunny",
                    )
                ],
                name=None,
            )
        ]
        result = json.loads(serialize_mirascope_messages(messages))
        assert result == [
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_output",
                        "id": "call_123",
                        "name": "get_weather",
                        "result": "72°F, sunny",
                    }
                ],
                "name": None,
            }
        ]

    def test_serialize_image_base64(self) -> None:
        """Test serialization of Image with Base64ImageSource."""
        messages = [
            UserMessage(
                content=[
                    Image(
                        source=Base64ImageSource(
                            type="base64_image_source",
                            data="iVBORw0KGgo...",
                            mime_type="image/png",
                        )
                    )
                ],
                name=None,
            )
        ]
        result = json.loads(serialize_mirascope_messages(messages))
        assert result[0]["content"][0] == {
            "type": "image",
            "source": {
                "type": "base64_image_source",
                "mime_type": "image/png",
                "data": "iVBORw0KGgo...",
            },
        }

    def test_serialize_image_url(self) -> None:
        """Test serialization of Image with URLImageSource."""
        messages = [
            UserMessage(
                content=[
                    Image(
                        source=URLImageSource(
                            type="url_image_source",
                            url="https://example.com/image.png",
                        )
                    )
                ],
                name=None,
            )
        ]
        result = json.loads(serialize_mirascope_messages(messages))
        assert result[0]["content"][0] == {
            "type": "image",
            "source": {
                "type": "url_image_source",
                "url": "https://example.com/image.png",
            },
        }

    def test_serialize_audio(self) -> None:
        """Test serialization of Audio content."""
        messages = [
            UserMessage(
                content=[
                    Audio(
                        source=Base64AudioSource(
                            type="base64_audio_source",
                            data="audio_data_here",
                            mime_type="audio/mp3",
                        )
                    )
                ],
                name=None,
            )
        ]
        result = json.loads(serialize_mirascope_messages(messages))
        assert result[0]["content"][0] == {
            "type": "audio",
            "source": {
                "type": "base64_audio_source",
                "mime_type": "audio/mp3",
                "data": "audio_data_here",
            },
        }

    def test_serialize_document_base64(self) -> None:
        """Test serialization of Document with Base64DocumentSource."""
        messages = [
            UserMessage(
                content=[
                    Document(
                        source=Base64DocumentSource(
                            type="base64_document_source",
                            data="pdf_data_here",
                            media_type="application/pdf",
                        )
                    )
                ],
                name=None,
            )
        ]
        result = json.loads(serialize_mirascope_messages(messages))
        assert result[0]["content"][0] == {
            "type": "document",
            "source": {
                "type": "base64_document_source",
                "data": "pdf_data_here",
                "media_type": "application/pdf",
            },
        }

    def test_serialize_document_text(self) -> None:
        """Test serialization of Document with TextDocumentSource."""
        messages = [
            UserMessage(
                content=[
                    Document(
                        source=TextDocumentSource(
                            type="text_document_source",
                            data="plain text content",
                            media_type="text/plain",
                        )
                    )
                ],
                name=None,
            )
        ]
        result = json.loads(serialize_mirascope_messages(messages))
        assert result[0]["content"][0] == {
            "type": "document",
            "source": {
                "type": "text_document_source",
                "data": "plain text content",
                "media_type": "text/plain",
            },
        }

    def test_serialize_document_url(self) -> None:
        """Test serialization of Document with URLDocumentSource."""
        messages = [
            UserMessage(
                content=[
                    Document(
                        source=URLDocumentSource(
                            type="url_document_source",
                            url="https://example.com/doc.pdf",
                        )
                    )
                ],
                name=None,
            )
        ]
        result = json.loads(serialize_mirascope_messages(messages))
        assert result[0]["content"][0] == {
            "type": "document",
            "source": {
                "type": "url_document_source",
                "url": "https://example.com/doc.pdf",
            },
        }


class TestSerializeUsage:
    """Tests for serialize_mirascope_usage function."""

    def test_serialize_usage(self) -> None:
        """Test serialization of Usage with all fields."""
        usage = Usage(
            input_tokens=100,
            output_tokens=50,
            cache_read_tokens=20,
            cache_write_tokens=10,
            reasoning_tokens=5,
        )
        result = json.loads(serialize_mirascope_usage(usage))  # type: ignore
        assert result == {
            "input_tokens": 100,
            "output_tokens": 50,
            "cache_read_tokens": 20,
            "cache_write_tokens": 10,
            "reasoning_tokens": 5,
            "total_tokens": 150,
        }

    def test_serialize_usage_defaults(self) -> None:
        """Test serialization of Usage with default values."""
        usage = Usage(input_tokens=10, output_tokens=5)
        result = json.loads(serialize_mirascope_usage(usage))  # type: ignore
        assert result == {
            "input_tokens": 10,
            "output_tokens": 5,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "total_tokens": 15,
        }

    def test_serialize_usage_none(self) -> None:
        """Test that None usage returns None."""
        assert serialize_mirascope_usage(None) is None


class TestSerializeCost:
    """Tests for serialize_mirascope_cost function."""

    def test_serialize_cost_all_fields(self) -> None:
        """Test serialization of cost with all fields."""
        result = json.loads(
            serialize_mirascope_cost(
                input_cost=25.0,
                output_cost=50.0,
                total_cost=80.0,
                cache_read_cost=3.0,
                cache_write_cost=2.0,
            )
        )
        assert result == {
            "input_cost": 25.0,
            "output_cost": 50.0,
            "cache_read_cost": 3.0,
            "cache_write_cost": 2.0,
            "total_cost": 80.0,
        }

    def test_serialize_cost_no_cache(self) -> None:
        """Test serialization of cost without cache fields."""
        result = json.loads(
            serialize_mirascope_cost(
                input_cost=100.0,
                output_cost=200.0,
                total_cost=300.0,
            )
        )
        assert result == {
            "input_cost": 100.0,
            "output_cost": 200.0,
            "cache_read_cost": None,
            "cache_write_cost": None,
            "total_cost": 300.0,
        }

    def test_serialize_cost_zero_values(self) -> None:
        """Test serialization of cost with zero values."""
        result = json.loads(
            serialize_mirascope_cost(
                input_cost=0.0,
                output_cost=0.0,
                total_cost=0.0,
            )
        )
        assert result["input_cost"] == 0.0
        assert result["output_cost"] == 0.0
        assert result["total_cost"] == 0.0


class MockSpan:
    """Mock span implementation for testing."""

    def __init__(self) -> None:
        self.attributes: dict[str, AttributeValue] = {}

    def set(self, **attributes: AttributeValue) -> None:
        """Set attributes on the span."""
        self.attributes.update(attributes)


def _make_mock_response(with_usage: bool = True) -> MagicMock:
    """Create a mock RootResponse for testing."""
    mock = MagicMock()
    mock.provider_id = "openai"
    mock.model_id = "openai/gpt-4o-mini"
    mock.pretty.return_value = "assistant: Hello, world!"
    mock.messages = [
        SystemMessage(content=Text(text="You are helpful.")),
        UserMessage(content=[Text(text="Hi")], name=None),
        AssistantMessage(
            content=[Text(text="Hello!")],
            name=None,
            provider_id="openai",
            model_id="openai/gpt-4o-mini",
            provider_model_name=None,
            raw_message=None,
        ),
    ]
    mock.content = [Text(text="Hello, world!")]
    if with_usage:
        mock.usage = Usage(input_tokens=100, output_tokens=50)
    else:
        mock.usage = None
    return mock


def _make_mock_cost_response(
    input_cost: float = 25.0,
    output_cost: float = 50.0,
    total_cost: float = 75.0,
    cache_read_cost: float | None = None,
    cache_write_cost: float | None = None,
) -> MagicMock:
    """Create a mock TokenCostCalculateResponse."""
    mock = MagicMock()
    mock.input_cost_centicents = input_cost
    mock.output_cost_centicents = output_cost
    mock.total_cost_centicents = total_cost
    mock.cache_read_cost_centicents = cache_read_cost
    mock.cache_write_cost_centicents = cache_write_cost
    return mock


class TestAttachMirascopeResponse:
    """Tests for attach_mirascope_response function."""

    def test_attach_response_with_cost(self) -> None:
        """Test attach_mirascope_response sets cost when cost calculation succeeds."""
        span = MockSpan()
        response = _make_mock_response(with_usage=True)
        mock_cost = _make_mock_cost_response(
            input_cost=25.0,
            output_cost=50.0,
            total_cost=75.0,
            cache_read_cost=5.0,
            cache_write_cost=10.0,
        )

        with patch(
            "mirascope.ops._internal.instrumentation.llm.serialize.calculate_cost_sync",
            return_value=mock_cost,
        ):
            attach_mirascope_response(span, response)

        # Verify cost was attached
        assert "mirascope.response.cost" in span.attributes
        cost_json = span.attributes["mirascope.response.cost"]
        assert isinstance(cost_json, str)
        cost_data = json.loads(cost_json)
        assert cost_data["input_cost"] == 25.0
        assert cost_data["output_cost"] == 50.0
        assert cost_data["total_cost"] == 75.0
        assert cost_data["cache_read_cost"] == 5.0
        assert cost_data["cache_write_cost"] == 10.0

    def test_attach_response_without_usage(self) -> None:
        """Test attach_mirascope_response when response has no usage."""
        span = MockSpan()
        response = _make_mock_response(with_usage=False)

        with patch(
            "mirascope.ops._internal.instrumentation.llm.serialize.calculate_cost_sync",
        ) as mock_calc:
            attach_mirascope_response(span, response)

        # Cost calculation should not be called when there's no usage
        mock_calc.assert_not_called()
        assert "mirascope.response.cost" not in span.attributes

    def test_attach_response_cost_calculation_returns_none(self) -> None:
        """Test attach_mirascope_response when cost calculation returns None."""
        span = MockSpan()
        response = _make_mock_response(with_usage=True)

        with patch(
            "mirascope.ops._internal.instrumentation.llm.serialize.calculate_cost_sync",
            return_value=None,
        ):
            attach_mirascope_response(span, response)

        # Cost should not be attached when calculation returns None
        assert "mirascope.response.cost" not in span.attributes


class TestAttachMirascopeResponseAsync:
    """Tests for attach_mirascope_response_async function."""

    @pytest.mark.asyncio
    async def test_attach_response_async_with_cost(self) -> None:
        """Test attach_mirascope_response_async sets cost when cost calculation succeeds."""
        span = MockSpan()
        response = _make_mock_response(with_usage=True)
        mock_cost = _make_mock_cost_response(
            input_cost=30.0,
            output_cost=60.0,
            total_cost=90.0,
            cache_read_cost=8.0,
            cache_write_cost=12.0,
        )

        with patch(
            "mirascope.ops._internal.instrumentation.llm.serialize.calculate_cost_async",
            new_callable=AsyncMock,
            return_value=mock_cost,
        ):
            await attach_mirascope_response_async(span, response)

        # Verify cost was attached
        assert "mirascope.response.cost" in span.attributes
        cost_json = span.attributes["mirascope.response.cost"]
        assert isinstance(cost_json, str)
        cost_data = json.loads(cost_json)
        assert cost_data["input_cost"] == 30.0
        assert cost_data["output_cost"] == 60.0
        assert cost_data["total_cost"] == 90.0
        assert cost_data["cache_read_cost"] == 8.0
        assert cost_data["cache_write_cost"] == 12.0

    @pytest.mark.asyncio
    async def test_attach_response_async_without_usage(self) -> None:
        """Test attach_mirascope_response_async when response has no usage."""
        span = MockSpan()
        response = _make_mock_response(with_usage=False)

        with patch(
            "mirascope.ops._internal.instrumentation.llm.serialize.calculate_cost_async",
            new_callable=AsyncMock,
        ) as mock_calc:
            await attach_mirascope_response_async(span, response)

        # Cost calculation should not be called when there's no usage
        mock_calc.assert_not_called()
        assert "mirascope.response.cost" not in span.attributes

    @pytest.mark.asyncio
    async def test_attach_response_async_cost_calculation_returns_none(self) -> None:
        """Test attach_mirascope_response_async when cost calculation returns None."""
        span = MockSpan()
        response = _make_mock_response(with_usage=True)

        with patch(
            "mirascope.ops._internal.instrumentation.llm.serialize.calculate_cost_async",
            new_callable=AsyncMock,
            return_value=None,
        ):
            await attach_mirascope_response_async(span, response)

        # Cost should not be attached when calculation returns None
        assert "mirascope.response.cost" not in span.attributes


class TestSerializeTools:
    """Tests for serialize_tools function."""

    def test_serialize_provider_tool(self) -> None:
        """Test serialization of ProviderTool."""
        tool = ProviderTool(name="test_tool")
        result = serialize_tools([tool])
        assert result == snapshot('[{"name":"test_tool","type":"extension"}]')
