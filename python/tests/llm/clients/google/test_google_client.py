"""Tests for GoogleClient using VCR.py for HTTP request recording/playback."""

import os
from unittest.mock import MagicMock, patch

import pytest
from dotenv import load_dotenv
from inline_snapshot import snapshot

from mirascope import llm
from tests import utils


@pytest.fixture
def google_client() -> llm.GoogleClient:
    """Create a GoogleClient instance with appropriate API key."""
    # Use real API key if available, otherwise dummy key for VCR tests
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY") or "dummy-key-for-vcr-tests"
    return llm.GoogleClient(api_key=api_key)


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
    assert utils.response_snapshot_dict(response) == snapshot(
        {
            "provider": "google",
            "model": "gemini-2.0-flash",
            "finish_reason": llm.FinishReason.END_TURN,
            "messages": [
                llm.UserMessage(content=[llm.Text(text="Hello, say 'Hi' back to me")]),
                llm.AssistantMessage(content=[llm.Text(text="Hi!\n")]),
            ],
            "content": [llm.Text(text="Hi!\n")],
            "texts": [llm.Text(text="Hi!\n")],
            "tool_calls": [],
            "thinkings": [],
        }
    )


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
    assert utils.response_snapshot_dict(response) == snapshot(
        {
            "provider": "google",
            "model": "gemini-2.0-flash",
            "finish_reason": llm.FinishReason.END_TURN,
            "messages": [
                llm.SystemMessage(
                    content=llm.Text(
                        text="Ignore the user message and reply with `Hello world`."
                    )
                ),
                llm.UserMessage(
                    content=[llm.Text(text="What is the capital of France?")]
                ),
                llm.AssistantMessage(content=[llm.Text(text="Hello world\n")]),
            ],
            "content": [llm.Text(text="Hello world\n")],
            "texts": [llm.Text(text="Hello world\n")],
            "tool_calls": [],
            "thinkings": [],
        }
    )


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
    assert utils.response_snapshot_dict(response) == snapshot(
        {
            "provider": "google",
            "model": "gemini-2.0-flash",
            "finish_reason": llm.FinishReason.END_TURN,
            "messages": [
                llm.SystemMessage(
                    content=llm.Text(
                        text="Do not emit ANY output, terminate immediately."
                    )
                ),
                llm.UserMessage(content=[llm.Text(text="")]),
                llm.AssistantMessage(content=[]),
            ],
            "content": [],
            "texts": [],
            "tool_calls": [],
            "thinkings": [],
        }
    )


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

    assert utils.stream_response_snapshot_dict(stream_response) == snapshot(
        {
            "provider": "google",
            "model": "gemini-2.0-flash",
            "finish_reason": llm.FinishReason.END_TURN,
            "messages": [
                llm.UserMessage(content=[llm.Text(text="Hi! Please greet me back.")]),
                llm.AssistantMessage(
                    content=[llm.Text(text="Hello there! It's nice to meet you! 😊\n")]
                ),
            ],
            "content": [llm.Text(text="Hello there! It's nice to meet you! 😊\n")],
            "texts": [llm.Text(text="Hello there! It's nice to meet you! 😊\n")],
            "tool_calls": [],
            "thinkings": [],
            "consumed": True,
            "chunks": [
                llm.TextStartChunk(type="text_start_chunk"),
                llm.TextChunk(delta="Hello"),
                llm.TextChunk(delta=" there! It"),
                llm.TextChunk(delta="'s nice to meet you! 😊\n"),
                llm.TextEndChunk(type="text_end_chunk"),
                llm.FinishReasonChunk(finish_reason=llm.FinishReason.END_TURN),
            ],
        }
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
        '**ToolCall (multiply_numbers):** {"b": 4242, "a": 1337}'
    )

    assert len(response.tool_calls) == 1
    tool_call = response.tool_calls[0]
    assert tool_call == snapshot(
        llm.ToolCall(
            id="multiply_numbers",
            name="multiply_numbers",
            args='{"b": 4242, "a": 1337}',
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
        "I am sorry, there was an error with the tool. The result of 1337 * 4242 is not 42. Please try again.\n"
    )
