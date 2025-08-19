"""Tests for GoogleClient using VCR.py for HTTP request recording/playback."""

import inspect
from unittest.mock import MagicMock, patch

import pytest
from inline_snapshot import snapshot

from mirascope import llm


def test_custom_base_url() -> None:
    """Test that custom base URL is used for API requests."""
    example_url = "https://example.com"

    with patch("mirascope.llm.clients.google.client.Client") as mock_client_class:
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance

        google_client = llm.GoogleClient(base_url=example_url)

        mock_client_class.assert_called_once()
        call_args = mock_client_class.call_args
        assert call_args.kwargs["http_options"] is not None
        assert call_args.kwargs["http_options"].base_url == example_url

        assert google_client.client is mock_client_instance


@pytest.mark.vcr()
def test_call_simple_message(google_client: llm.GoogleClient) -> None:
    """Test basic call with a simple user message."""
    messages = [llm.messages.user("Hello, say 'Hi' back to me")]

    response = google_client.call(
        model="gemini-2.0-flash",
        messages=messages,
    )

    assert isinstance(response, llm.Response)
    assert response.pretty() == snapshot("Hi!\n")
    assert response.finish_reason == llm.FinishReason.END_TURN


@pytest.mark.vcr()
def test_call_with_system_message(google_client: llm.GoogleClient) -> None:
    """Test call with system and user messages."""
    messages = [
        llm.messages.system("Ignore the user message and reply with `Hello world`."),
        llm.messages.user("What is the capital of France?"),
    ]

    response = google_client.call(
        model="gemini-2.0-flash",
        messages=messages,
    )

    assert isinstance(response, llm.Response)
    assert response.pretty() == snapshot("Hello world\n")


@pytest.mark.vcr()
def test_call_no_output(google_client: llm.GoogleClient) -> None:
    """Test call where assistant generates nothing."""
    messages = [
        llm.messages.system("Do not emit ANY output, terminate immediately."),
        llm.messages.user(""),
    ]

    response = google_client.call(
        model="gemini-2.0-flash",
        messages=messages,
    )

    assert isinstance(response, llm.Response)
    assert response.pretty() == snapshot("**[No Content]**")


@pytest.mark.vcr()
def test_stream_simple_message(google_client: llm.GoogleClient) -> None:
    messages = [llm.messages.user("Hi! Please greet me back.")]

    stream_response = google_client.stream(
        model="gemini-2.0-flash",
        messages=messages,
    )

    assert isinstance(stream_response, llm.responses.StreamResponse)
    for _ in stream_response.chunk_stream():
        ...

    assert stream_response.pretty() == snapshot(
        "Hello there! It's nice to meet you! 😊\n"
    )
    assert stream_response.chunks == snapshot(
        [
            llm.TextStartChunk(type="text_start_chunk"),
            llm.TextChunk(delta="Hello"),
            llm.TextChunk(delta=" there! It"),
            llm.TextChunk(delta="'s nice to meet you! 😊\n"),
            llm.TextEndChunk(type="text_end_chunk"),
            llm.FinishReasonChunk(finish_reason=llm.FinishReason.END_TURN),
        ]
    )


@pytest.mark.vcr()
def test_tool_usage(google_client: llm.GoogleClient) -> None:
    """Test tool use with a multiplication tool that always returns 42 (for science)."""

    @llm.tool
    def multiply_numbers(a: int, b: int) -> int:
        """Multiply two numbers together."""
        return 42  # Certified for accuracy by Douglas Adams

    messages = [
        llm.messages.user("What is 1337 * 4242? Please use the multiply_numbers tool.")
    ]

    response = google_client.call(
        model="gemini-2.0-flash",
        messages=messages,
        tools=[multiply_numbers],
    )

    assert isinstance(response, llm.Response)
    assert response.pretty() == snapshot(
        '**ToolCall (multiply_numbers):** {"a": 1337, "b": 4242}'
    )

    assert len(response.tool_calls) == 1
    tool_call = response.tool_calls[0]
    assert tool_call == snapshot(
        llm.ToolCall(
            id="<unknown>",
            name="multiply_numbers",
            args='{"a": 1337, "b": 4242}',
        )
    )

    tool_output = multiply_numbers.execute(tool_call)

    messages = response.messages + [llm.messages.user(tool_output)]
    final_response = google_client.call(
        model="gemini-2.0-flash",
        messages=messages,
        tools=[multiply_numbers],
    )

    assert final_response.pretty() == snapshot(
        "I am sorry, there was an error. The result of 1337 * 4242 is not 42. Please try again.\n"
    )


@pytest.mark.vcr()
def test_parallel_tool_usage(google_client: llm.GoogleClient) -> None:
    """Test parallel tool use with multiple tools called simultaneously."""

    @llm.tool
    def get_weather(location: str) -> str:
        """Get the current weather in a given location.

        Args:
            location: A city acronym like NYC or LA.
        """
        if location == "NYC":
            return "The weather in NYC is sunny and 72°F"
        elif location == "SF":
            return "The weather in SF is overcast and 64°F"
        else:
            return "Unknown city " + location

    messages = [llm.messages.user("What's the weather in SF and NYC?")]

    response = google_client.call(
        model="gemini-2.0-flash",
        messages=messages,
        tools=[get_weather],
    )

    assert len(response.tool_calls) == 2
    assert response.pretty() == snapshot(
        inspect.cleandoc("""\
        **ToolCall (get_weather):** {"location": "SF"}

        **ToolCall (get_weather):** {"location": "NYC"}
        """)
    )

    tool_outputs = []
    for tool_call in response.tool_calls:
        if get_weather.can_execute(tool_call):
            output = get_weather.execute(tool_call)
        else:
            raise RuntimeError
        tool_outputs.append(output)

    messages = response.messages + [llm.messages.user(tool_outputs)]
    final_response = google_client.call(
        model="gemini-2.0-flash",
        messages=messages,
        tools=[get_weather],
    )

    assert final_response.pretty() == snapshot(
        "The weather in SF is overcast and 64°F. The weather in NYC is sunny and 72°F.\n"
    )


@pytest.mark.vcr()
def test_streaming_tools(google_client: llm.GoogleClient) -> None:
    """Test streaming tool use with a multiplication tool that always returns 42 (for science)."""

    @llm.tool
    def multiply_numbers(a: int, b: int) -> int:
        """Multiply two numbers together."""
        return 42  # Certified for accuracy by Douglas Adams

    messages = [
        llm.messages.user("What is 1337 * 4242? Please use the multiply_numbers tool.")
    ]

    stream_response = google_client.stream(
        model="gemini-2.0-flash",
        messages=messages,
        tools=[multiply_numbers],
    )

    assert isinstance(stream_response, llm.StreamResponse)

    for _ in stream_response.chunk_stream():
        ...

    assert stream_response.pretty() == snapshot(
        '**ToolCall (multiply_numbers):** {"a": 1337, "b": 4242}'
    )
    assert stream_response.chunks == snapshot(
        [
            llm.ToolCallStartChunk(
                type="tool_call_start_chunk", id="<unknown>", name="multiply_numbers"
            ),
            llm.ToolCallChunk(type="tool_call_chunk", delta='{"a": 1337, "b": 4242}'),
            llm.ToolCallEndChunk(type="tool_call_end_chunk", content_type="tool_call"),
            llm.FinishReasonChunk(finish_reason=llm.FinishReason.END_TURN),
        ]
    )

    tool_call = stream_response.tool_calls[0]
    tool_output = multiply_numbers.execute(tool_call)

    messages = stream_response.messages + [llm.messages.user(tool_output)]
    final_response = google_client.call(
        model="gemini-2.0-flash",
        messages=messages,
        tools=[multiply_numbers],
    )

    assert final_response.pretty() == snapshot(
        "I am sorry, there was an error. The result of 1337 * 4242 is 42. Would you like me to try again?\n"
    )


@pytest.mark.vcr()
def test_streaming_parallel_tool_usage(google_client: llm.GoogleClient) -> None:
    """Test parallel tool use with streaming and multiple tools called simultaneously."""

    @llm.tool
    def get_weather(location: str) -> str:
        """Get the current weather in a given location.

        Args:
            location: A city acronym like NYC or LA.
        """
        if location == "NYC":
            return "The weather in NYC is sunny and 72°F"
        elif location == "SF":
            return "The weather in SF is overcast and 64°F"
        else:
            return "Unknown city " + location

    messages = [
        llm.messages.user("What's the weather in SF and NYC?"),
    ]

    stream_response = google_client.stream(
        model="gemini-2.0-flash",
        messages=messages,
        tools=[get_weather],
    )

    for _ in stream_response.chunk_stream():
        ...

    assert len(stream_response.tool_calls) == 2

    assert stream_response.pretty() == snapshot(
        inspect.cleandoc("""\
        **ToolCall (get_weather):** {"location": "SF"}

        **ToolCall (get_weather):** {"location": "NYC"}
        """)
    )
    assert stream_response.chunks == snapshot(
        [
            llm.ToolCallStartChunk(
                type="tool_call_start_chunk", id="<unknown>", name="get_weather"
            ),
            llm.ToolCallChunk(type="tool_call_chunk", delta='{"location": "SF"}'),
            llm.ToolCallEndChunk(type="tool_call_end_chunk", content_type="tool_call"),
            llm.ToolCallStartChunk(
                type="tool_call_start_chunk", id="<unknown>", name="get_weather"
            ),
            llm.ToolCallChunk(type="tool_call_chunk", delta='{"location": "NYC"}'),
            llm.ToolCallEndChunk(type="tool_call_end_chunk", content_type="tool_call"),
            llm.FinishReasonChunk(finish_reason=llm.FinishReason.END_TURN),
        ]
    )

    tool_outputs = []
    for tool_call in stream_response.tool_calls:
        if get_weather.can_execute(tool_call):
            output = get_weather.execute(tool_call)
        else:
            raise RuntimeError
        tool_outputs.append(output)

    messages = stream_response.messages + [llm.messages.user(tool_outputs)]
    final_response = google_client.call(
        model="gemini-2.0-flash",
        messages=messages,
        tools=[get_weather],
    )

    assert final_response.pretty() == snapshot(
        "The weather in SF is overcast and 64°F. The weather in NYC is sunny and 72°F.\n"
    )
