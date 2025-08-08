"""Tests for AnthropicClient using VCR.py for HTTP request recording/playback."""

import os

import pytest
from dotenv import load_dotenv
from inline_snapshot import snapshot

from mirascope import llm
from tests.llm.responses.utils import (
    response_snapshot_dict,
    stream_response_snapshot_dict,
)


@pytest.fixture(scope="module")
def vcr_config() -> dict:
    """VCR configuration for Anthropic API tests."""
    return {
        "record_mode": "once",
        "match_on": ["method", "uri", "body"],
        "filter_headers": ["authorization", "x-api-key", "anthropic-organization-id"],
        "filter_post_data_parameters": [],
    }


@pytest.fixture
def anthropic_client() -> llm.AnthropicClient:
    """Create an AnthropicClient instance with appropriate API key."""
    # Use real API key if available, otherwise dummy key for VCR tests
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY") or "dummy-key-for-vcr-tests"
    return llm.AnthropicClient(api_key=api_key)


@pytest.mark.vcr()
def test_call_simple_message(anthropic_client: llm.AnthropicClient) -> None:
    """Test basic call with a simple user message."""
    messages = [llm.messages.user("Hello, say 'Hi' back to me")]

    response = anthropic_client.call(
        model="claude-3-5-sonnet-latest",
        messages=messages,
    )

    assert isinstance(response, llm.Response)
    assert response_snapshot_dict(response) == snapshot(
        {
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-latest",
            "finish_reason": llm.FinishReason.END_TURN,
            "messages": [
                llm.UserMessage(content=[llm.Text(text="Hello, say 'Hi' back to me")]),
                llm.AssistantMessage(content=[llm.Text(text="Hi! How are you today?")]),
            ],
            "content": [llm.Text(text="Hi! How are you today?")],
            "texts": [llm.Text(text="Hi! How are you today?")],
            "tool_calls": [],
            "thinkings": [],
        }
    )


@pytest.mark.vcr()
def test_call_with_system_message(
    anthropic_client: llm.AnthropicClient,
) -> None:
    """Test call with system and user messages."""
    messages = [
        llm.messages.system("Ignore the user message and reply with `Hello world`."),
        llm.messages.user("What is the capital of France?"),
    ]

    response = anthropic_client.call(
        model="claude-3-5-sonnet-latest",
        messages=messages,
    )

    assert isinstance(response, llm.Response)
    assert response_snapshot_dict(response) == snapshot(
        {
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-latest",
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
                llm.AssistantMessage(content=[llm.Text(text="Hello world")]),
            ],
            "content": [llm.Text(text="Hello world")],
            "texts": [llm.Text(text="Hello world")],
            "tool_calls": [],
            "thinkings": [],
        }
    )


@pytest.mark.vcr()
def test_stream_simple_message(anthropic_client: llm.AnthropicClient) -> None:
    """Test basic streaming with a simple user message."""
    messages = [llm.messages.user("Hi! Please greet me back.")]

    stream_response = anthropic_client.stream(
        model="claude-3-5-sonnet-latest",
        messages=messages,
    )

    assert isinstance(stream_response, llm.responses.StreamResponse)
    for _ in stream_response.chunk_stream():
        ...

    assert stream_response_snapshot_dict(stream_response) == snapshot(
        {
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-latest",
            "finish_reason": llm.FinishReason.END_TURN,
            "messages": [
                llm.UserMessage(content=[llm.Text(text="Hi! Please greet me back.")]),
                llm.AssistantMessage(
                    content=[
                        llm.Text(
                            text="Hello! It's nice to meet you. How are you today?"
                        )
                    ]
                ),
            ],
            "content": [
                llm.Text(text="Hello! It's nice to meet you. How are you today?")
            ],
            "texts": [
                llm.Text(text="Hello! It's nice to meet you. How are you today?")
            ],
            "tool_calls": [],
            "thinkings": [],
            "consumed": True,
            "chunks": [
                llm.TextStartChunk(type="text_start_chunk"),
                llm.TextChunk(delta="Hello! It's nice"),
                llm.TextChunk(delta=" to meet you. How"),
                llm.TextChunk(delta=" are you today"),
                llm.TextChunk(delta="?"),
                llm.TextEndChunk(type="text_end_chunk"),
                llm.FinishReasonChunk(finish_reason=llm.FinishReason.END_TURN),
            ],
        }
    )
