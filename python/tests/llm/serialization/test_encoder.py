"""Tests for serialization encoder."""

import json
from typing import cast

import msgspec
from inline_snapshot import snapshot
from pydantic import BaseModel

from mirascope import llm
from mirascope.llm.providers import Params, ProviderId
from mirascope.llm.content import Text, Thought, ToolCall
from mirascope.llm.messages import AssistantMessage, SystemMessage, UserMessage
from mirascope.llm.responses import FinishReason, Response
from mirascope.llm.serialization import encode, encode_str
from mirascope.llm.serialization._generated.response import (
    FinishReason as SerializedFinishReason,
)
from mirascope.llm.serialization.encoder import (
    _encode_finish_reason,  # pyright: ignore[reportPrivateUsage]
    _encode_format,  # pyright: ignore[reportPrivateUsage]
    _encode_message,  # pyright: ignore[reportPrivateUsage]
    _encode_tools,  # pyright: ignore[reportPrivateUsage]
)
from mirascope.llm.tools import Toolkit


def _create_test_response(
    *,
    provider_id: str = "anthropic",
    model_id: str = "claude-sonnet-4-20250514",
    finish_reason: FinishReason | None = None,
) -> Response[None]:
    """Create a test response for testing."""
    input_messages = [
        SystemMessage(content=Text(text="You are a helpful assistant.")),
        UserMessage(content=[Text(text="Hello!")]),
    ]
    assistant_message = AssistantMessage(
        content=[Text(text="Hello! How can I help?")],
        provider_id=cast(ProviderId, provider_id),
        model_id=model_id,
        provider_model_name=model_id,
        raw_message=None,
    )
    return Response(
        raw=None,
        provider_id=cast(ProviderId, provider_id),
        model_id=model_id,
        provider_model_name=model_id,
        params=cast(Params, {}),
        tools=None,
        format=None,
        input_messages=input_messages,
        assistant_message=assistant_message,
        finish_reason=finish_reason,
    )


def test_encode_finish_reason() -> None:
    """Test encoding finish reasons."""
    assert _encode_finish_reason(None) is None
    assert (
        _encode_finish_reason(FinishReason.MAX_TOKENS)
        == SerializedFinishReason.max_tokens
    )
    assert _encode_finish_reason(FinishReason.REFUSAL) == SerializedFinishReason.refusal


def test_encode_message_system() -> None:
    """Test encoding SystemMessage."""
    msg = SystemMessage(content=Text(text="You are helpful."))
    result = _encode_message(msg)
    assert msgspec.json.decode(msgspec.json.encode(result)) == snapshot(
        {"role": "system", "content": [{"type": "text", "text": "You are helpful."}]}
    )


def test_encode_message_user() -> None:
    """Test encoding UserMessage."""
    msg = UserMessage(content=[Text(text="Hello!")], name="user1")
    result = _encode_message(msg)
    assert msgspec.json.decode(msgspec.json.encode(result)) == snapshot(
        {
            "role": "user",
            "content": [{"type": "text", "text": "Hello!"}],
            "name": "user1",
        }
    )


def test_encode_message_user_no_name() -> None:
    """Test encoding UserMessage without name."""
    msg = UserMessage(content=[Text(text="Hello!")])
    result = _encode_message(msg)
    assert msgspec.json.decode(msgspec.json.encode(result)) == snapshot(
        {"role": "user", "content": [{"type": "text", "text": "Hello!"}], "name": None}
    )


def test_encode_message_assistant() -> None:
    """Test encoding AssistantMessage."""
    msg = AssistantMessage(
        content=[Text(text="Hi!"), Thought(thought="Thinking...")],
        name="assistant1",
        provider_id="anthropic",
        model_id="claude-sonnet-4-20250514",
        provider_model_name="claude-sonnet-4-20250514",
        raw_message={"id": "msg_123"},
    )
    result = _encode_message(msg)
    assert msgspec.json.decode(msgspec.json.encode(result)) == snapshot(
        {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "Hi!"},
                {"type": "thought", "thought": "Thinking..."},
            ],
            "name": "assistant1",
            "provider": "anthropic",
            "model_id": "claude-sonnet-4-20250514",
            "raw_message": {"id": "msg_123"},
        }
    )


def test_encode_returns_bytes() -> None:
    """Test that encode returns bytes."""
    response = _create_test_response()
    encoded = encode(response)
    assert isinstance(encoded, bytes)


def test_encode_str_returns_string() -> None:
    """Test that encode_str returns a string."""
    response = _create_test_response()
    encoded = encode_str(response)
    assert isinstance(encoded, str)


def test_encode_structure() -> None:
    """Test encoded output structure."""
    response = _create_test_response(
        provider_id="openai",
        model_id="gpt-4o",
        finish_reason=FinishReason.MAX_TOKENS,
    )
    encoded = encode_str(response)
    data = json.loads(encoded)

    assert data["$schema"] == snapshot("mirascope/response/v1")
    assert data["version"] == snapshot("1.0")
    assert data["type"] == snapshot("response")
    assert data["provider"] == snapshot("openai")
    assert data["model_id"] == snapshot("gpt-4o")
    assert data["finish_reason"] == snapshot("max_tokens")
    assert data["messages"] == snapshot(
        [
            {
                "role": "system",
                "content": [{"type": "text", "text": "You are a helpful assistant."}],
            },
            {
                "role": "user",
                "content": [{"type": "text", "text": "Hello!"}],
                "name": None,
            },
            {
                "role": "assistant",
                "content": [{"type": "text", "text": "Hello! How can I help?"}],
                "name": None,
                "provider": "openai",
                "model_id": "gpt-4o",
                "raw_message": None,
            },
        ]
    )
    assert "serialized_at" in data["metadata"]
    assert "mirascope_version" in data["metadata"]


def test_encode_with_custom_version() -> None:
    """Test encoding with custom version."""
    response = _create_test_response()
    encoded = encode_str(response, version="1.5")
    data = json.loads(encoded)
    assert data["version"] == snapshot("1.5")


def test_encode_with_tool_calls() -> None:
    """Test encoding response with tool calls."""
    input_messages = [UserMessage(content=[Text(text="What's the weather?")])]
    assistant_message = AssistantMessage(
        content=[
            Text(text="Let me check the weather."),
            ToolCall(id="call_1", name="get_weather", args='{"city": "Tokyo"}'),
        ],
        provider_id="anthropic",
        model_id="claude-sonnet-4-20250514",
        provider_model_name="claude-sonnet-4-20250514",
        raw_message=None,
    )
    response = Response(
        raw=None,
        provider_id="anthropic",
        model_id="claude-sonnet-4-20250514",
        provider_model_name="claude-sonnet-4-20250514",
        params=cast(Params, {}),
        tools=None,
        format=None,
        input_messages=input_messages,
        assistant_message=assistant_message,
        finish_reason=None,
    )

    encoded = encode_str(response)
    data = json.loads(encoded)

    assert data["messages"][-1]["content"] == snapshot(
        [
            {"type": "text", "text": "Let me check the weather."},
            {
                "type": "tool_call",
                "id": "call_1",
                "name": "get_weather",
                "args": '{"city": "Tokyo"}',
            },
        ]
    )


def test_encode_tools_with_toolkit() -> None:
    """Test encoding tools from a toolkit."""

    @llm.tool
    def get_weather(city: str) -> str:
        """Get weather for a city.

        Args:
            city: The city name.
        """
        return f"Weather in {city}"

    @llm.tool
    def get_time(timezone: str) -> str:
        """Get current time.

        Args:
            timezone: The timezone.
        """
        return f"Time in {timezone}"

    toolkit = Toolkit(tools=[get_weather, get_time])
    encoded = _encode_tools(toolkit)
    assert encoded is not None
    assert msgspec.json.decode(msgspec.json.encode(encoded)) == snapshot(
        [
            {
                "name": "get_weather",
                "description": "Get weather for a city.\n\nArgs:\n    city: The city name.",
                "parameters": {
                    "properties": {
                        "city": {
                            "description": "The city name.",
                            "title": "City",
                            "type": "string",
                        }
                    },
                    "required": ["city"],
                    "additionalProperties": False,
                },
                "strict": False,
            },
            {
                "name": "get_time",
                "description": "Get current time.\n\nArgs:\n    timezone: The timezone.",
                "parameters": {
                    "properties": {
                        "timezone": {
                            "description": "The timezone.",
                            "title": "Timezone",
                            "type": "string",
                        }
                    },
                    "required": ["timezone"],
                    "additionalProperties": False,
                },
                "strict": False,
            },
        ]
    )


def test_encode_tools_empty_toolkit() -> None:
    """Test encoding empty toolkit returns None."""
    toolkit = Toolkit(tools=None)
    encoded = _encode_tools(toolkit)
    assert encoded is None


def test_encode_format() -> None:
    """Test encoding a format."""

    class Book(BaseModel):
        """A book."""

        title: str
        author: str

    format_obj = llm.format(Book, mode="tool")
    encoded = _encode_format(format_obj)
    assert encoded is not None
    assert msgspec.json.decode(msgspec.json.encode(encoded)) == snapshot(
        {
            "name": "Book",
            "description": "A book.",
            "schema": {
                "description": "A book.",
                "properties": {
                    "title": {"title": "Title", "type": "string"},
                    "author": {"title": "Author", "type": "string"},
                },
                "required": ["title", "author"],
                "title": "Book",
                "type": "object",
            },
            "mode": "tool",
        }
    )


def test_encode_format_none() -> None:
    """Test encoding None format returns None."""
    encoded = _encode_format(None)
    assert encoded is None


def test_encode_response_with_tools() -> None:
    """Test encoding response with tools."""

    @llm.tool
    def get_weather(city: str) -> str:
        """Get weather for a city.

        Args:
            city: The city name.
        """
        return f"Weather in {city}"

    input_messages = [UserMessage(content=[Text(text="What's the weather?")])]
    assistant_message = AssistantMessage(
        content=[Text(text="Let me check.")],
        provider_id="anthropic",
        model_id="claude-sonnet-4-20250514",
        provider_model_name="claude-sonnet-4-20250514",
        raw_message=None,
    )
    response = Response(
        raw=None,
        provider_id="anthropic",
        model_id="claude-sonnet-4-20250514",
        provider_model_name="claude-sonnet-4-20250514",
        params=cast(Params, {}),
        tools=[get_weather],
        format=None,
        input_messages=input_messages,
        assistant_message=assistant_message,
        finish_reason=None,
    )

    encoded = encode_str(response)
    data = json.loads(encoded)

    assert data["tools"] == snapshot(
        [
            {
                "name": "get_weather",
                "description": "Get weather for a city.\n\nArgs:\n    city: The city name.",
                "parameters": {
                    "properties": {
                        "city": {
                            "description": "The city name.",
                            "title": "City",
                            "type": "string",
                        }
                    },
                    "required": ["city"],
                    "additionalProperties": False,
                },
                "strict": False,
            }
        ]
    )


def test_encode_response_with_format() -> None:
    """Test encoding response with format."""

    class Book(BaseModel):
        """A book."""

        title: str
        author: str

    input_messages = [UserMessage(content=[Text(text="Recommend a book")])]
    assistant_message = AssistantMessage(
        content=[Text(text='{"title": "1984", "author": "George Orwell"}')],
        provider_id="anthropic",
        model_id="claude-sonnet-4-20250514",
        provider_model_name="claude-sonnet-4-20250514",
        raw_message=None,
    )
    response = Response(
        raw=None,
        provider_id="anthropic",
        model_id="claude-sonnet-4-20250514",
        provider_model_name="claude-sonnet-4-20250514",
        params=cast(Params, {}),
        tools=None,
        format=llm.format(Book, mode="tool"),
        input_messages=input_messages,
        assistant_message=assistant_message,
        finish_reason=None,
    )

    encoded = encode_str(response)
    data = json.loads(encoded)

    assert data["format"] == snapshot(
        {
            "name": "Book",
            "description": "A book.",
            "schema": {
                "description": "A book.",
                "properties": {
                    "title": {"title": "Title", "type": "string"},
                    "author": {"title": "Author", "type": "string"},
                },
                "required": ["title", "author"],
                "title": "Book",
                "type": "object",
            },
            "mode": "tool",
        }
    )
