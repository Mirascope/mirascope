"""Tests for serialization decoder."""

import json
from typing import Any

import msgspec
import pytest
from inline_snapshot import snapshot
from pydantic import BaseModel

from mirascope import llm
from mirascope.llm.content import Text, Thought, ToolCall, ToolOutput
from mirascope.llm.messages import AssistantMessage, SystemMessage, UserMessage
from mirascope.llm.responses import FinishReason, Response
from mirascope.llm.serialization import decode
from mirascope.llm.serialization._generated.response import (
    AssistantMessage as SerializedAssistantMessage,
    FinishReason as SerializedFinishReason,
    SystemMessage as SerializedSystemMessage,
    TextContent,
    ThoughtContent,
    ToolCallContent,
    ToolOutputContent,
    UserMessage as SerializedUserMessage,
)
from mirascope.llm.serialization.decoder import (
    _decode_assistant_content_part,  # pyright: ignore[reportPrivateUsage]
    _decode_finish_reason,  # pyright: ignore[reportPrivateUsage]
    _decode_message,  # pyright: ignore[reportPrivateUsage]
    _decode_user_content_part,  # pyright: ignore[reportPrivateUsage]
)
from mirascope.llm.serialization.exceptions import (
    IncompatibleFormatError,
    IncompatibleToolsError,
    IncompatibleVersionError,
    InvalidSerializedDataError,
)
from mirascope.llm.serialization.version import CURRENT_VERSION


def _create_minimal_payload(
    *,
    version: str = CURRENT_VERSION,
    response_type: str = "response",
    provider: str = "anthropic",
    model_id: str = "claude-sonnet-4-20250514",
    finish_reason: str | None = None,
) -> dict[str, Any]:
    """Create a minimal valid payload for testing."""
    return {
        "$schema": f"mirascope/response/v{version.split('.')[0]}",
        "version": version,
        "type": response_type,
        "provider": provider,
        "model_id": model_id,
        "finish_reason": finish_reason,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": "Hello!"}],
                "name": None,
            },
            {
                "role": "assistant",
                "content": [{"type": "text", "text": "Hi there!"}],
                "name": None,
                "provider": provider,
                "model_id": model_id,
                "raw_message": None,
            },
        ],
        "params": None,
        "metadata": {
            "serialized_at": "2024-01-01T00:00:00Z",
            "mirascope_version": "2.0.0",
        },
    }


def test_decode_finish_reason() -> None:
    """Test decoding finish reasons."""
    assert _decode_finish_reason(None) == snapshot(None)
    assert _decode_finish_reason(msgspec.UNSET) == snapshot(None)
    assert _decode_finish_reason(SerializedFinishReason.max_tokens) == snapshot(
        FinishReason.MAX_TOKENS
    )
    assert _decode_finish_reason(SerializedFinishReason.refusal) == snapshot(
        FinishReason.REFUSAL
    )


def test_decode_message_system() -> None:
    """Test decoding SystemMessage."""
    data = SerializedSystemMessage(
        content=[TextContent(text="You are helpful.")],
    )
    msg = _decode_message(data)
    assert isinstance(msg, SystemMessage)
    assert msg.content == snapshot(Text(text="You are helpful."))


def test_decode_message_user() -> None:
    """Test decoding UserMessage."""
    data = SerializedUserMessage(
        content=[TextContent(text="Hello!")],
        name="user1",
    )
    msg = _decode_message(data)
    assert isinstance(msg, UserMessage)
    assert msg.content == snapshot([Text(text="Hello!")])
    assert msg.name == snapshot("user1")


def test_decode_message_assistant() -> None:
    """Test decoding AssistantMessage."""
    data = SerializedAssistantMessage(
        content=[
            TextContent(text="Hi!"),
            ThoughtContent(thought="Thinking..."),
        ],
        name="assistant1",
        provider="anthropic",
        model_id="claude-sonnet-4-20250514",
        raw_message={"id": "msg_123"},
    )
    msg = _decode_message(data)
    assert isinstance(msg, AssistantMessage)
    assert msg == snapshot(
        AssistantMessage(
            content=[Text(text="Hi!"), Thought(thought="Thinking...")],
            name="assistant1",
            provider_id="anthropic",
            model_id="claude-sonnet-4-20250514",
            provider_model_name="claude-sonnet-4-20250514",
            raw_message={"id": "msg_123"},
        )
    )


def test_decode_message_unknown_role_raises() -> None:
    """Test that unknown role raises exception via public API."""
    payload = _create_minimal_payload()
    payload["messages"][0]["role"] = "unknown"
    data = json.dumps(payload).encode("utf-8")
    with pytest.raises(InvalidSerializedDataError):
        decode(data)


def test_decode_returns_response() -> None:
    """Test that decode returns a Response."""
    payload = _create_minimal_payload()
    data = json.dumps(payload).encode("utf-8")
    response = decode(data)
    assert isinstance(response, Response)


def test_decode_str_returns_response() -> None:
    """Test that decode with string returns a Response."""
    payload = _create_minimal_payload()
    data = json.dumps(payload)
    response = decode(data)
    assert isinstance(response, Response)


def test_decode_response_structure() -> None:
    """Test decoded response structure."""
    payload = _create_minimal_payload(
        provider="openai",
        model_id="gpt-4o",
        finish_reason="max_tokens",
    )
    data = json.dumps(payload).encode("utf-8")
    response = decode(data)

    assert (response.provider_id, response.model_id, response.finish_reason) == snapshot(
        ("openai", "gpt-4o", FinishReason.MAX_TOKENS)
    )
    assert len(response.messages) == snapshot(2)
    assert isinstance(response.messages[0], UserMessage)
    assert isinstance(response.messages[1], AssistantMessage)
    assert response.toolkit.tools == snapshot([])
    assert response.format == snapshot(None)
    assert response.raw == snapshot(None)


def test_decode_missing_version_raises() -> None:
    """Test that missing version raises exception."""
    payload = _create_minimal_payload()
    del payload["version"]
    data = json.dumps(payload).encode("utf-8")
    with pytest.raises(InvalidSerializedDataError):
        decode(data)


def test_decode_incompatible_version_raises() -> None:
    """Test that incompatible version raises exception."""
    payload = _create_minimal_payload(version="2.0")
    data = json.dumps(payload).encode("utf-8")
    with pytest.raises(IncompatibleVersionError):
        decode(data)


def test_decode_invalid_version_format_raises() -> None:
    """Test that invalid version format raises exception."""
    payload = _create_minimal_payload()
    payload["version"] = "invalid"
    data = json.dumps(payload).encode("utf-8")
    with pytest.raises(InvalidSerializedDataError):
        decode(data)


def test_decode_compatible_minor_version() -> None:
    """Test that compatible minor version works."""
    payload = _create_minimal_payload(version="1.5")
    data = json.dumps(payload).encode("utf-8")
    response = decode(data)
    assert isinstance(response, Response)


def test_decode_schema_mismatch_raises() -> None:
    """Test that schema mismatch raises exception."""
    payload = _create_minimal_payload(version="1.0")
    payload["$schema"] = "mirascope/response/v2"
    data = json.dumps(payload).encode("utf-8")
    with pytest.raises(InvalidSerializedDataError, match="Schema mismatch"):
        decode(data)


def test_decode_invalid_json_raises() -> None:
    """Test that invalid JSON raises exception."""
    data = b"not valid json"
    with pytest.raises(InvalidSerializedDataError, match="Invalid JSON"):
        decode(data)


def test_decode_unknown_type_raises() -> None:
    """Test that unknown response type raises exception."""
    payload = _create_minimal_payload(response_type="unknown")
    data = json.dumps(payload).encode("utf-8")
    with pytest.raises(InvalidSerializedDataError):
        decode(data)


def test_decode_no_messages_raises() -> None:
    """Test that empty messages raises exception."""
    payload = _create_minimal_payload()
    payload["messages"] = []
    data = json.dumps(payload).encode("utf-8")
    with pytest.raises(InvalidSerializedDataError):
        decode(data)


def test_decode_no_assistant_message_raises() -> None:
    """Test that missing assistant message raises exception."""
    payload = _create_minimal_payload()
    payload["messages"] = [
        {
            "role": "user",
            "content": [{"type": "text", "text": "Hello!"}],
            "name": None,
        }
    ]
    data = json.dumps(payload).encode("utf-8")
    with pytest.raises(InvalidSerializedDataError, match="Last message must be"):
        decode(data)


def test_decode_missing_provider_raises() -> None:
    """Test that missing provider raises InvalidSerializedDataError."""
    payload = _create_minimal_payload()
    del payload["provider"]
    data = json.dumps(payload).encode("utf-8")
    with pytest.raises(InvalidSerializedDataError):
        decode(data)


def test_decode_missing_model_id_raises() -> None:
    """Test that missing model_id raises InvalidSerializedDataError."""
    payload = _create_minimal_payload()
    del payload["model_id"]
    data = json.dumps(payload).encode("utf-8")
    with pytest.raises(InvalidSerializedDataError):
        decode(data)


def test_decode_user_content_part() -> None:
    """Test decoding user content parts."""
    assert _decode_user_content_part(TextContent(text="Hello")) == snapshot(
        Text(text="Hello")
    )
    assert _decode_user_content_part(
        ToolOutputContent(id="call_1", name="tool", value={"result": 42})
    ) == snapshot(ToolOutput(id="call_1", name="tool", value={"result": 42}))


def test_decode_assistant_content_part() -> None:
    """Test decoding assistant content parts."""
    assert _decode_assistant_content_part(TextContent(text="Hi")) == snapshot(
        Text(text="Hi")
    )
    assert _decode_assistant_content_part(
        ToolCallContent(id="call_1", name="get_weather", args='{"city": "Tokyo"}')
    ) == snapshot(ToolCall(id="call_1", name="get_weather", args='{"city": "Tokyo"}'))
    assert _decode_assistant_content_part(
        ThoughtContent(thought="Thinking...")
    ) == snapshot(Thought(thought="Thinking..."))


def test_decode_with_tool_calls() -> None:
    """Test decoding response with tool calls."""
    payload = _create_minimal_payload()
    payload["messages"][-1]["content"] = [
        {"type": "text", "text": "Let me check."},
        {"type": "tool_call", "id": "call_1", "name": "get_weather", "args": "{}"},
    ]
    data = json.dumps(payload).encode("utf-8")
    response = decode(data)

    assert response.content == snapshot(
        [
            Text(text="Let me check."),
            ToolCall(id="call_1", name="get_weather", args="{}"),
        ]
    )
    assert response.tool_calls == snapshot(
        [ToolCall(id="call_1", name="get_weather", args="{}")]
    )


def test_decode_tool_calls_list() -> None:
    """Test that tool_calls is populated correctly."""
    payload = _create_minimal_payload()
    payload["messages"][-1]["content"] = [
        {"type": "tool_call", "id": "call_1", "name": "tool1", "args": "{}"},
        {"type": "tool_call", "id": "call_2", "name": "tool2", "args": "{}"},
    ]
    data = json.dumps(payload).encode("utf-8")
    response = decode(data)

    assert response.tool_calls == snapshot(
        [
            ToolCall(id="call_1", name="tool1", args="{}"),
            ToolCall(id="call_2", name="tool2", args="{}"),
        ]
    )


def test_decode_with_tools() -> None:
    """Test decoding with tools provided."""

    @llm.tool
    def get_weather(city: str) -> str:
        """Get weather for a city.

        Args:
            city: The city name.
        """
        return f"Weather in {city}"

    payload = _create_minimal_payload()
    payload["tools"] = [
        {
            "name": "get_weather",
            "description": "Get weather for a city.",
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
    data = json.dumps(payload).encode("utf-8")
    response = decode(data, tools=[get_weather])

    assert len(response.toolkit.tools) == snapshot(1)
    assert response.toolkit.tools[0].name == snapshot("get_weather")


def test_decode_with_format() -> None:
    """Test decoding with format provided."""

    class Book(BaseModel):
        """A book."""

        title: str
        author: str

    format_obj = llm.format(Book, mode="tool")
    assert format_obj is not None
    payload = _create_minimal_payload()
    payload["format"] = {
        "name": "Book",
        "description": "A book.",
        "schema": format_obj.schema,
        "mode": "tool",
    }
    data = json.dumps(payload).encode("utf-8")
    response = decode(data, format=format_obj)

    assert response.format is not None
    assert response.format.name == snapshot("Book")


def test_decode_tools_missing_raises() -> None:
    """Test that missing tools raises IncompatibleToolsError."""
    payload = _create_minimal_payload()
    payload["tools"] = [
        {
            "name": "get_weather",
            "description": "Get weather.",
            "parameters": {
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
                "additionalProperties": False,
            },
            "strict": False,
        }
    ]
    data = json.dumps(payload).encode("utf-8")

    with pytest.raises(IncompatibleToolsError) as exc_info:
        decode(data)

    assert (
        exc_info.value.field,
        "no tools were provided" in str(exc_info.value),
    ) == snapshot(("tools", True))


def test_decode_tools_not_superset_raises() -> None:
    """Test that tools not being a superset raises IncompatibleToolsError."""

    @llm.tool
    def different_tool(x: int) -> int:
        """Different tool."""
        return x

    payload = _create_minimal_payload()
    payload["tools"] = [
        {
            "name": "get_weather",
            "description": "Get weather.",
            "parameters": {
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
                "additionalProperties": False,
            },
            "strict": False,
        }
    ]
    data = json.dumps(payload).encode("utf-8")

    with pytest.raises(IncompatibleToolsError) as exc_info:
        decode(data, tools=[different_tool])

    assert (
        exc_info.value.field,
        "not found in provided tools" in str(exc_info.value),
    ) == snapshot(("tools", True))


def test_decode_tools_schema_mismatch_raises() -> None:
    """Test that schema mismatch raises IncompatibleToolsError."""

    @llm.tool
    def get_weather(temperature: float) -> str:
        """Get weather."""
        return str(temperature)

    payload = _create_minimal_payload()
    payload["tools"] = [
        {
            "name": "get_weather",
            "description": "Get weather.",
            "parameters": {
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
                "additionalProperties": False,
            },
            "strict": False,
        }
    ]
    data = json.dumps(payload).encode("utf-8")

    with pytest.raises(IncompatibleToolsError) as exc_info:
        decode(data, tools=[get_weather])

    assert (
        exc_info.value.field,
        "properties mismatch" in str(exc_info.value),
    ) == snapshot(("tools", True))


def test_decode_tools_additional_properties_mismatch_raises() -> None:
    """Test that additionalProperties mismatch raises IncompatibleToolsError."""

    @llm.tool
    def get_weather(city: str) -> str:
        """Get weather."""
        return city

    payload = _create_minimal_payload()
    payload["tools"] = [
        {
            "name": "get_weather",
            "description": "Get weather.",
            "parameters": {
                "properties": {
                    "city": {
                        "title": "City",
                        "type": "string",
                    }
                },
                "required": ["city"],
                "additionalProperties": True,
            },
            "strict": False,
        }
    ]
    data = json.dumps(payload).encode("utf-8")

    with pytest.raises(IncompatibleToolsError) as exc_info:
        decode(data, tools=[get_weather])

    assert (
        exc_info.value.field,
        "additionalProperties mismatch" in str(exc_info.value),
    ) == snapshot(("tools", True))


def test_decode_tools_strict_mismatch_raises() -> None:
    """Test that strict mode mismatch raises IncompatibleToolsError."""

    @llm.tool
    def get_weather(city: str) -> str:
        """Get weather."""
        return city

    payload = _create_minimal_payload()
    payload["tools"] = [
        {
            "name": "get_weather",
            "description": "Get weather.",
            "parameters": {
                "properties": {
                    "city": {
                        "title": "City",
                        "type": "string",
                    }
                },
                "required": ["city"],
                "additionalProperties": False,
            },
            "strict": True,
        }
    ]
    data = json.dumps(payload).encode("utf-8")

    with pytest.raises(IncompatibleToolsError) as exc_info:
        decode(data, tools=[get_weather])

    assert (
        exc_info.value.field,
        "strict mode mismatch" in str(exc_info.value),
    ) == snapshot(("tools", True))


def test_decode_format_missing_raises() -> None:
    """Test that missing format raises IncompatibleFormatError."""
    payload = _create_minimal_payload()
    payload["format"] = {
        "name": "Book",
        "description": "A book.",
        "schema": {"properties": {"title": {"type": "string"}}},
        "mode": "tool",
    }
    data = json.dumps(payload).encode("utf-8")

    with pytest.raises(IncompatibleFormatError) as exc_info:
        decode(data)

    assert (
        exc_info.value.field,
        "no format was provided" in str(exc_info.value),
    ) == snapshot(("format", True))


def test_decode_format_schema_mismatch_raises() -> None:
    """Test that format schema mismatch raises IncompatibleFormatError."""

    class DifferentBook(BaseModel):
        """Different book."""

        isbn: str

    format_obj = llm.format(DifferentBook, mode="tool")
    payload = _create_minimal_payload()
    payload["format"] = {
        "name": "Book",
        "description": "A book.",
        "schema": {"properties": {"title": {"type": "string"}}},
        "mode": "tool",
    }
    data = json.dumps(payload).encode("utf-8")

    with pytest.raises(IncompatibleFormatError) as exc_info:
        decode(data, format=format_obj)

    assert (exc_info.value.field, "schema mismatch" in str(exc_info.value)) == snapshot(
        ("format", True)
    )


def test_decode_tools_superset_allowed() -> None:
    """Test that tools can be a superset of serialized tools."""

    @llm.tool
    def get_weather(city: str) -> str:
        """Get weather.

        Args:
            city: The city.
        """
        return city

    @llm.tool
    def extra_tool(x: int) -> int:
        """Extra tool not in serialized data."""
        return x

    payload = _create_minimal_payload()
    payload["tools"] = [
        {
            "name": "get_weather",
            "description": "Get weather.",
            "parameters": {
                "properties": {
                    "city": {
                        "description": "The city.",
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
    data = json.dumps(payload).encode("utf-8")

    response = decode(data, tools=[get_weather, extra_tool])
    assert [t.name for t in response.toolkit.tools] == snapshot(
        ["get_weather", "extra_tool"]
    )
