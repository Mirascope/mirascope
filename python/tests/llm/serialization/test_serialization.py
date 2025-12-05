"""Tests for encode/decode roundtrip."""

from typing import Any, cast

from inline_snapshot import snapshot
from pydantic import BaseModel

from mirascope import llm
from mirascope.llm.providers import Params, ProviderId
from mirascope.llm.content import (
    Audio,
    Base64AudioSource,
    Base64ImageSource,
    Image,
    Text,
    Thought,
    ToolCall,
    ToolOutput,
    URLImageSource,
)
from mirascope.llm.messages import AssistantMessage, SystemMessage, UserMessage
from mirascope.llm.responses import FinishReason, Response
from mirascope.llm.serialization import decode, encode


def _create_response(
    *,
    input_messages: list[Any],
    assistant_content: list[Any],
    provider_id: str = "anthropic",
    model_id: str = "claude-sonnet-4-20250514",
    finish_reason: FinishReason | None = None,
    params: dict[str, Any] | None = None,
) -> Response[None]:
    """Create a test response."""
    assistant_message = AssistantMessage(
        content=assistant_content,
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
        params=cast(Params, params if params is not None else {}),
        tools=None,
        format=None,
        input_messages=input_messages,
        assistant_message=assistant_message,
        finish_reason=finish_reason,
    )


def test_roundtrip_simple_text() -> None:
    """Test roundtrip with simple text content."""
    original = _create_response(
        input_messages=[
            UserMessage(content=[Text(text="Hello!")]),
        ],
        assistant_content=[Text(text="Hi there!")],
    )

    decoded = decode(encode(original))

    assert (decoded.provider_id, decoded.model_id) == snapshot(
        ("anthropic", "claude-sonnet-4-20250514")
    )
    assert decoded.messages == snapshot(
        [
            UserMessage(content=[Text(text="Hello!")]),
            AssistantMessage(
                content=[Text(text="Hi there!")],
                provider_id="anthropic",
                model_id="claude-sonnet-4-20250514",
                provider_model_name="claude-sonnet-4-20250514",
                raw_message=None,
            ),
        ]
    )


def test_roundtrip_with_system_message() -> None:
    """Test roundtrip with system message."""
    original = _create_response(
        input_messages=[
            SystemMessage(content=Text(text="You are helpful.")),
            UserMessage(content=[Text(text="Hello!")]),
        ],
        assistant_content=[Text(text="Hi!")],
    )

    decoded = decode(encode(original))

    assert decoded.messages == snapshot(
        [
            SystemMessage(content=Text(text="You are helpful.")),
            UserMessage(content=[Text(text="Hello!")]),
            AssistantMessage(
                content=[Text(text="Hi!")],
                provider_id="anthropic",
                model_id="claude-sonnet-4-20250514",
                provider_model_name="claude-sonnet-4-20250514",
                raw_message=None,
            ),
        ]
    )


def test_roundtrip_with_thoughts() -> None:
    """Test roundtrip with thought content."""
    original = _create_response(
        input_messages=[
            UserMessage(content=[Text(text="Think about this.")]),
        ],
        assistant_content=[
            Thought(thought="Let me think about this carefully..."),
            Text(text="Here's my answer."),
        ],
    )

    decoded = decode(encode(original))

    assert decoded.content == snapshot(
        [
            Thought(thought="Let me think about this carefully..."),
            Text(text="Here's my answer."),
        ]
    )
    assert decoded.thoughts == snapshot(
        [Thought(thought="Let me think about this carefully...")]
    )


def test_roundtrip_with_tool_calls() -> None:
    """Test roundtrip with tool call content."""
    original = _create_response(
        input_messages=[
            UserMessage(content=[Text(text="What's the weather?")]),
        ],
        assistant_content=[
            Text(text="Let me check."),
            ToolCall(id="call_1", name="get_weather", args='{"city": "Tokyo"}'),
        ],
    )

    decoded = decode(encode(original))

    assert decoded.tool_calls == snapshot(
        [ToolCall(id="call_1", name="get_weather", args='{"city": "Tokyo"}')]
    )


def test_roundtrip_with_tool_output() -> None:
    """Test roundtrip with tool output in user message."""
    original = _create_response(
        input_messages=[
            UserMessage(content=[Text(text="What's the weather?")]),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_1",
                        name="get_weather",
                        value={"temp": 22, "condition": "sunny"},
                    )
                ]
            ),
        ],
        assistant_content=[Text(text="It's 22°C and sunny!")],
    )

    decoded = decode(encode(original))

    assert decoded.messages[1] == snapshot(
        UserMessage(
            content=[
                ToolOutput(
                    id="call_1",
                    name="get_weather",
                    value={"temp": 22, "condition": "sunny"},
                )
            ]
        )
    )


def test_roundtrip_with_image_base64() -> None:
    """Test roundtrip with base64 image."""
    original = _create_response(
        input_messages=[
            UserMessage(
                content=[
                    Image(
                        source=Base64ImageSource(
                            type="base64_image_source",
                            data="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                            mime_type="image/png",
                        )
                    ),
                    Text(text="What's in this image?"),
                ]
            ),
        ],
        assistant_content=[Text(text="I see an image.")],
    )

    decoded = decode(encode(original))
    user_msg = decoded.messages[0]

    assert isinstance(user_msg, UserMessage)
    assert user_msg.content == snapshot(
        [
            Image(
                source=Base64ImageSource(
                    type="base64_image_source",
                    data="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                    mime_type="image/png",
                )
            ),
            Text(text="What's in this image?"),
        ]
    )


def test_roundtrip_with_image_url() -> None:
    """Test roundtrip with URL image."""
    original = _create_response(
        input_messages=[
            UserMessage(
                content=[
                    Image(
                        source=URLImageSource(
                            type="url_image_source",
                            url="https://example.com/image.png",
                        )
                    ),
                ]
            ),
        ],
        assistant_content=[Text(text="I see the image.")],
    )

    decoded = decode(encode(original))
    user_msg = decoded.messages[0]

    assert isinstance(user_msg, UserMessage)
    assert user_msg.content == snapshot(
        [
            Image(
                source=URLImageSource(
                    type="url_image_source",
                    url="https://example.com/image.png",
                )
            )
        ]
    )


def test_roundtrip_with_audio() -> None:
    """Test roundtrip with audio content."""
    original = _create_response(
        input_messages=[
            UserMessage(
                content=[
                    Audio(
                        source=Base64AudioSource(
                            type="base64_audio_source",
                            data="UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=",
                            mime_type="audio/wav",
                        )
                    ),
                ]
            ),
        ],
        assistant_content=[Text(text="I heard audio.")],
    )

    decoded = decode(encode(original))
    user_msg = decoded.messages[0]

    assert isinstance(user_msg, UserMessage)
    assert user_msg.content == snapshot(
        [
            Audio(
                source=Base64AudioSource(
                    type="base64_audio_source",
                    data="UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=",
                    mime_type="audio/wav",
                )
            )
        ]
    )


def test_roundtrip_with_finish_reason() -> None:
    """Test roundtrip preserves finish reason."""
    original = _create_response(
        input_messages=[UserMessage(content=[Text(text="Write a long story.")])],
        assistant_content=[Text(text="Once upon a time...")],
        finish_reason=FinishReason.MAX_TOKENS,
    )

    decoded = decode(encode(original))

    assert decoded.finish_reason == snapshot(FinishReason.MAX_TOKENS)


def test_roundtrip_with_message_names() -> None:
    """Test roundtrip preserves message names."""
    original = _create_response(
        input_messages=[
            UserMessage(content=[Text(text="Hello!")], name="alice"),
        ],
        assistant_content=[Text(text="Hi Alice!")],
    )

    decoded = decode(encode(original))

    assert decoded.messages[0] == snapshot(
        UserMessage(content=[Text(text="Hello!")], name="alice")
    )


def test_roundtrip_preserves_raw_message() -> None:
    """Test roundtrip preserves raw_message in AssistantMessage."""
    assistant_message = AssistantMessage(
        content=[Text(text="Hi!")],
        provider_id="anthropic",
        model_id="claude-sonnet-4-20250514",
        provider_model_name="claude-sonnet-4-20250514",
        raw_message={"id": "msg_123", "type": "message"},
    )
    original = Response(
        raw=None,
        provider_id="anthropic",
        model_id="claude-sonnet-4-20250514",
        provider_model_name="claude-sonnet-4-20250514",
        params=cast(Params, {}),
        tools=None,
        format=None,
        input_messages=[UserMessage(content=[Text(text="Hello!")])],
        assistant_message=assistant_message,
        finish_reason=None,
    )

    decoded = decode(encode(original))

    assert decoded.messages[-1] == snapshot(
        AssistantMessage(
            content=[Text(text="Hi!")],
            provider_id="anthropic",
            model_id="claude-sonnet-4-20250514",
            provider_model_name="claude-sonnet-4-20250514",
            raw_message={"id": "msg_123", "type": "message"},
        )
    )


def test_roundtrip_multiple_providers() -> None:
    """Test roundtrip works with different providers."""
    providers = ["anthropic", "openai", "google", "azure", "bedrock"]

    for provider_id in providers:
        original = _create_response(
            input_messages=[UserMessage(content=[Text(text="Hello!")])],
            assistant_content=[Text(text="Hi!")],
            provider_id=provider_id,
        )

        decoded = decode(encode(original))

        assert decoded.provider_id == provider_id


def test_roundtrip_params_none() -> None:
    """Test roundtrip with None params converts to empty dict."""
    assistant_message = AssistantMessage(
        content=[Text(text="Hi!")],
        provider_id="anthropic",
        model_id="claude-sonnet-4-20250514",
        provider_model_name="claude-sonnet-4-20250514",
        raw_message=None,
    )
    original = Response(
        raw=None,
        provider_id="anthropic",
        model_id="claude-sonnet-4-20250514",
        provider_model_name="claude-sonnet-4-20250514",
        params=cast(Params, {}),
        tools=None,
        format=None,
        input_messages=[UserMessage(content=[Text(text="Hello!")])],
        assistant_message=assistant_message,
        finish_reason=None,
    )

    decoded = decode(encode(original))

    assert decoded.params == snapshot({})


def test_roundtrip_params_empty_dict() -> None:
    """Test roundtrip preserves empty dict params."""
    original = _create_response(
        input_messages=[UserMessage(content=[Text(text="Hello!")])],
        assistant_content=[Text(text="Hi!")],
        params={},
    )

    decoded = decode(encode(original))

    assert decoded.params == snapshot({})


def test_roundtrip_params_with_values() -> None:
    """Test roundtrip preserves params with values."""
    original = _create_response(
        input_messages=[UserMessage(content=[Text(text="Hello!")])],
        assistant_content=[Text(text="Hi!")],
        params={"temperature": 0.7, "max_tokens": 100},
    )

    decoded = decode(encode(original))

    assert decoded.params == snapshot({"temperature": 0.7, "max_tokens": 100})


def test_response_encode_method() -> None:
    """Test Response.encode() method returns bytes."""
    response = _create_response(
        input_messages=[UserMessage(content=[Text(text="Hello!")])],
        assistant_content=[Text(text="Hi!")],
    )

    encoded = response.encode()
    assert isinstance(encoded, bytes)


def test_response_encode_str_method() -> None:
    """Test Response.encode_str() method returns string."""
    response = _create_response(
        input_messages=[UserMessage(content=[Text(text="Hello!")])],
        assistant_content=[Text(text="Hi!")],
    )

    encoded = response.encode_str()
    assert isinstance(encoded, str)


def test_response_decode_method() -> None:
    """Test Response.decode() class method."""
    original = _create_response(
        input_messages=[UserMessage(content=[Text(text="Hello!")])],
        assistant_content=[Text(text="Hi!")],
    )

    decoded = Response.decode(original.encode())

    assert isinstance(decoded, Response)
    assert decoded.provider_id == snapshot("anthropic")


def test_response_decode_from_string() -> None:
    """Test Response.decode() class method with string input."""
    original = _create_response(
        input_messages=[UserMessage(content=[Text(text="Hello!")])],
        assistant_content=[Text(text="Hi!")],
    )

    decoded = Response.decode(original.encode_str())

    assert isinstance(decoded, Response)
    assert decoded.provider_id == snapshot("anthropic")


def test_response_methods_roundtrip() -> None:
    """Test full roundtrip using Response methods."""
    original = _create_response(
        input_messages=[
            SystemMessage(content=Text(text="Be helpful.")),
            UserMessage(content=[Text(text="Hello!")]),
        ],
        assistant_content=[
            Thought(thought="Greeting the user..."),
            Text(text="Hi there! How can I help?"),
        ],
    )

    decoded = Response.decode(original.encode())

    assert (decoded.provider_id, decoded.model_id) == snapshot(
        ("anthropic", "claude-sonnet-4-20250514")
    )
    assert decoded.messages == snapshot(
        [
            SystemMessage(content=Text(text="Be helpful.")),
            UserMessage(content=[Text(text="Hello!")]),
            AssistantMessage(
                content=[
                    Thought(thought="Greeting the user..."),
                    Text(text="Hi there! How can I help?"),
                ],
                provider_id="anthropic",
                model_id="claude-sonnet-4-20250514",
                provider_model_name="claude-sonnet-4-20250514",
                raw_message=None,
            ),
        ]
    )


def test_roundtrip_with_tools() -> None:
    """Test roundtrip with tools."""

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

    assistant_message = AssistantMessage(
        content=[
            Text(text="Let me check."),
            ToolCall(id="call_1", name="get_weather", args='{"city": "Tokyo"}'),
        ],
        provider_id="anthropic",
        model_id="claude-sonnet-4-20250514",
        provider_model_name="claude-sonnet-4-20250514",
        raw_message=None,
    )
    original = Response(
        raw=None,
        provider_id="anthropic",
        model_id="claude-sonnet-4-20250514",
        provider_model_name="claude-sonnet-4-20250514",
        params={},
        tools=[get_weather, get_time],
        format=None,
        input_messages=[UserMessage(content=[Text(text="What's the weather?")])],
        assistant_message=assistant_message,
        finish_reason=None,
    )

    decoded = decode(encode(original), tools=[get_weather, get_time])

    assert (decoded.provider_id, decoded.model_id) == snapshot(
        ("anthropic", "claude-sonnet-4-20250514")
    )
    assert [t.name for t in decoded.toolkit.tools] == snapshot(
        ["get_weather", "get_time"]
    )
    assert decoded.tool_calls == snapshot(
        [ToolCall(id="call_1", name="get_weather", args='{"city": "Tokyo"}')]
    )


def test_roundtrip_with_format() -> None:
    """Test roundtrip with format."""

    class Book(BaseModel):
        """A book."""

        title: str
        author: str

    format_obj = llm.format(Book, mode="tool")

    assistant_message = AssistantMessage(
        content=[Text(text='{"title": "1984", "author": "George Orwell"}')],
        provider_id="anthropic",
        model_id="claude-sonnet-4-20250514",
        provider_model_name="claude-sonnet-4-20250514",
        raw_message=None,
    )
    original = Response(
        raw=None,
        provider_id="anthropic",
        model_id="claude-sonnet-4-20250514",
        provider_model_name="claude-sonnet-4-20250514",
        params={},
        tools=None,
        format=format_obj,
        input_messages=[UserMessage(content=[Text(text="Recommend a book")])],
        assistant_message=assistant_message,
        finish_reason=None,
    )

    decoded = decode(encode(original), format=format_obj)

    assert (
        decoded.provider_id,
        decoded.format.name if decoded.format else None,
    ) == snapshot(("anthropic", "Book"))
    assert decoded.parse() == snapshot(Book(title="1984", author="George Orwell"))


def test_roundtrip_with_tools_and_format() -> None:
    """Test roundtrip with both tools and format."""

    @llm.tool
    def search_books(query: str) -> str:
        """Search for books."""
        return query

    class BookList(BaseModel):
        """A list of books."""

        books: list[str]

    format_obj = llm.format(BookList, mode="tool")

    assistant_message = AssistantMessage(
        content=[Text(text='{"books": ["1984", "Brave New World"]}')],
        provider_id="anthropic",
        model_id="claude-sonnet-4-20250514",
        provider_model_name="claude-sonnet-4-20250514",
        raw_message=None,
    )
    original = Response(
        raw=None,
        provider_id="anthropic",
        model_id="claude-sonnet-4-20250514",
        provider_model_name="claude-sonnet-4-20250514",
        params={},
        tools=[search_books],
        format=format_obj,
        input_messages=[UserMessage(content=[Text(text="Find dystopian books")])],
        assistant_message=assistant_message,
        finish_reason=None,
    )

    decoded = decode(encode(original), tools=[search_books], format=format_obj)

    assert (
        decoded.provider_id,
        decoded.toolkit.tools[0].name,
        decoded.format.name if decoded.format else None,
    ) == snapshot(("anthropic", "search_books", "BookList"))
    assert decoded.parse() == snapshot(BookList(books=["1984", "Brave New World"]))
