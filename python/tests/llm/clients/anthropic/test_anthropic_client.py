"""Tests for AnthropicClient using VCR.py for HTTP request recording/playback."""

import os

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
from mirascope.llm.content import (
    FinishReasonChunk,
    TextChunk,
    TextEndChunk,
    TextStartChunk,
)
from tests.llm.responses._utils import stream_response_snapshot_dict


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration for Anthropic API tests."""
    return {
        "record_mode": "once",
        "match_on": ["method", "uri", "body"],
        "filter_headers": ["authorization", "x-api-key", "anthropic-organization-id"],
        "filter_post_data_parameters": [],
    }


@pytest.fixture
def anthropic_client():
    """Create an AnthropicClient instance with appropriate API key."""
    # Use real API key if available, otherwise dummy key for VCR tests
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY") or "dummy-key-for-vcr-tests"
    return llm.clients.AnthropicClient(api_key=api_key)


@pytest.mark.vcr()
def test_call_simple_message(anthropic_client):
    """Test basic call with a simple user message."""
    messages = [llm.messages.user("Hello, say 'Hi' back to me")]

    response = anthropic_client.call(
        model="claude-3-5-sonnet-latest",
        messages=messages,
    )

    assert isinstance(response, llm.responses.Response)
    response.__dict__.pop("raw")
    assert response.__dict__ == snapshot(
        {
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-latest",
            "finish_reason": FinishReason.END_TURN,
            "messages": [
                UserMessage(content=[Text(text="Hello, say 'Hi' back to me")]),
                AssistantMessage(content=[Text(text="Hi! How are you today?")]),
            ],
            "content": [Text(text="Hi! How are you today?")],
            "texts": [Text(text="Hi! How are you today?")],
            "tool_calls": [],
            "thinkings": [],
        }
    )


@pytest.mark.vcr()
def test_call_with_system_message(anthropic_client):
    """Test call with system and user messages."""
    messages = [
        llm.messages.system("Ignore the user message and reply with `Hello world`."),
        llm.messages.user("What is the capital of France?"),
    ]

    response = anthropic_client.call(
        model="claude-3-5-sonnet-latest",
        messages=messages,
    )

    assert isinstance(response, llm.responses.Response)
    response.__dict__.pop("raw")
    assert response.__dict__ == snapshot(
        {
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-latest",
            "finish_reason": FinishReason.END_TURN,
            "messages": [
                SystemMessage(
                    content=Text(
                        text="Ignore the user message and reply with `Hello world`."
                    )
                ),
                UserMessage(content=[Text(text="What is the capital of France?")]),
                AssistantMessage(content=[Text(text="Hello world")]),
            ],
            "content": [Text(text="Hello world")],
            "texts": [Text(text="Hello world")],
            "tool_calls": [],
            "thinkings": [],
        }
    )


@pytest.mark.vcr()
def test_stream_simple_message(anthropic_client):
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
            "finish_reason": FinishReason.END_TURN,
            "messages": [
                UserMessage(content=[Text(text="Hi! Please greet me back.")]),
                AssistantMessage(
                    content=[
                        Text(text="Hello! It's nice to meet you. How are you today?")
                    ]
                ),
            ],
            "content": [Text(text="Hello! It's nice to meet you. How are you today?")],
            "texts": [Text(text="Hello! It's nice to meet you. How are you today?")],
            "tool_calls": [],
            "thinkings": [],
            "consumed": True,
            "chunks": [
                TextStartChunk(type="text_start_chunk"),
                TextChunk(delta="Hello! It's nice"),
                TextChunk(delta=" to meet you. How"),
                TextChunk(delta=" are you today"),
                TextChunk(delta="?"),
                TextEndChunk(type="text_end_chunk"),
                FinishReasonChunk(finish_reason=FinishReason.END_TURN),
            ],
        }
    )
