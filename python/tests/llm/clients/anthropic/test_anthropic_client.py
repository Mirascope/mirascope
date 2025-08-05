"""Tests for AnthropicClient using VCR.py for HTTP request recording/playback."""

import os

import pytest
from anthropic.types import Message, TextBlock, Usage
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
        model="anthropic:claude-3-5-sonnet-latest",
        messages=messages,
    )

    assert isinstance(response, llm.responses.Response)

    assert response.messages == snapshot(
        [
            UserMessage(content=[Text(text="Hello, say 'Hi' back to me")]),
            AssistantMessage(content=[Text(text="Hi! How are you today?")]),
        ]
    )
    assert response.content == snapshot([Text(text="Hi! How are you today?")])
    assert response.finish_reason == snapshot(FinishReason.END_TURN)

    assert response.raw == snapshot(
        Message(
            id="msg_017D2Ft64FYt2ePjarbY9f1s",
            content=[TextBlock(text="Hi! How are you today?", type="text")],
            model="claude-3-5-sonnet-20241022",
            role="assistant",
            stop_reason="end_turn",
            type="message",
            usage=Usage(
                cache_creation_input_tokens=0,
                cache_read_input_tokens=0,
                input_tokens=17,
                output_tokens=10,
                service_tier="standard",
            ),
        )
    )


@pytest.mark.vcr()
def test_call_with_system_message(anthropic_client):
    """Test call with system and user messages."""
    messages = [
        llm.messages.system("Ignore the user message and reply with `Hello world`."),
        llm.messages.user("What is the capital of France?"),
    ]

    response = anthropic_client.call(
        model="anthropic:claude-3-5-sonnet-latest",
        messages=messages,
    )

    assert isinstance(response, llm.responses.Response)

    assert response.messages == snapshot(
        [
            SystemMessage(
                content=Text(
                    text="Ignore the user message and reply with `Hello world`."
                )
            ),
            UserMessage(content=[Text(text="What is the capital of France?")]),
            AssistantMessage(content=[Text(text="Hello world")]),
        ]
    )
    assert response.content == snapshot([Text(text="Hello world")])
    assert response.finish_reason == snapshot(FinishReason.END_TURN)

    assert response.raw == snapshot(
        Message(
            id="msg_01EbPjNBhocqRtYk5KHFStWx",
            content=[TextBlock(text="Hello world", type="text")],
            model="claude-3-5-sonnet-20241022",
            role="assistant",
            stop_reason="end_turn",
            type="message",
            usage=Usage(
                cache_creation_input_tokens=0,
                cache_read_input_tokens=0,
                input_tokens=26,
                output_tokens=5,
                service_tier="standard",
            ),
        )
    )
