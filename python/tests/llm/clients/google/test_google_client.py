"""Tests for GoogleClient using VCR.py for HTTP request recording/playback."""

import os
from unittest.mock import MagicMock, patch

import pytest
from dotenv import load_dotenv
from inline_snapshot import snapshot

from mirascope import llm
from mirascope.llm import (
    AssistantMessage,
    FinishReason,
    SystemMessage,
    Text,
    UserMessage,
)


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration for Google API tests."""
    return {
        "record_mode": "once",
        "match_on": ["method", "uri", "body"],
        "filter_headers": ["authorization", "x-goog-api-key"],
        "filter_post_data_parameters": [],
    }


@pytest.fixture
def google_client():
    """Create a GoogleClient instance with appropriate API key."""
    # Use real API key if available, otherwise dummy key for VCR tests
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY") or "dummy-key-for-vcr-tests"
    return llm.clients.GoogleClient(api_key=api_key)


def test_custom_base_url():
    """Test that custom base URL is used for API requests."""
    example_url = "https://example.com"

    with patch("mirascope.llm.clients.google.client.Client") as mock_client_class:
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance

        google_client = llm.clients.GoogleClient(base_url=example_url)

        mock_client_class.assert_called_once()
        call_args = mock_client_class.call_args
        assert call_args.kwargs["http_options"] is not None
        assert call_args.kwargs["http_options"].base_url == example_url

        assert google_client.client is mock_client_instance


@pytest.mark.vcr()
def test_call_simple_message(google_client):
    """Test basic call with a simple user message."""
    messages = [llm.messages.user("Hello, say 'Hi' back to me")]

    response = google_client.call(
        model="gemini-2.0-flash",
        messages=messages,
    )

    assert isinstance(response, llm.responses.Response)
    assert {k: v for k, v in response.__dict__.items() if k != "raw"} == snapshot(
        {
            "provider": "google",
            "model": "gemini-2.0-flash",
            "finish_reason": FinishReason.END_TURN,
            "messages": [
                UserMessage(content=[Text(text="Hello, say 'Hi' back to me")]),
                AssistantMessage(content=[Text(text="Hi!\n")]),
            ],
            "content": [Text(text="Hi!\n")],
            "texts": [Text(text="Hi!\n")],
            "tool_calls": [],
            "thinkings": [],
        }
    )


@pytest.mark.vcr()
def test_call_with_system_message(google_client):
    """Test call with system and user messages."""
    messages = [
        llm.messages.system("Ignore the user message and reply with `Hello world`."),
        llm.messages.user("What is the capital of France?"),
    ]

    response = google_client.call(
        model="gemini-2.0-flash",
        messages=messages,
    )

    assert isinstance(response, llm.responses.Response)
    assert {k: v for k, v in response.__dict__.items() if k != "raw"} == snapshot(
        {
            "provider": "google",
            "model": "gemini-2.0-flash",
            "finish_reason": FinishReason.END_TURN,
            "messages": [
                SystemMessage(
                    content=Text(
                        text="Ignore the user message and reply with `Hello world`."
                    )
                ),
                UserMessage(content=[Text(text="What is the capital of France?")]),
                AssistantMessage(content=[Text(text="Hello world\n")]),
            ],
            "content": [Text(text="Hello world\n")],
            "texts": [Text(text="Hello world\n")],
            "tool_calls": [],
            "thinkings": [],
        }
    )


@pytest.mark.vcr()
def test_call_no_output(google_client):
    """Test call where assistant generates nothing."""
    messages = [
        llm.messages.system("Do not emit ANY output, terminate immediately."),
        llm.messages.user(""),
    ]

    response = google_client.call(
        model="gemini-2.0-flash",
        messages=messages,
    )

    assert isinstance(response, llm.responses.Response)
    assert {k: v for k, v in response.__dict__.items() if k != "raw"} == snapshot(
        {
            "provider": "google",
            "model": "gemini-2.0-flash",
            "finish_reason": FinishReason.END_TURN,
            "messages": [
                SystemMessage(
                    content=Text(text="Do not emit ANY output, terminate immediately.")
                ),
                UserMessage(content=[Text(text="")]),
                AssistantMessage(content=[]),
            ],
            "content": [],
            "texts": [],
            "tool_calls": [],
            "thinkings": [],
        }
    )
