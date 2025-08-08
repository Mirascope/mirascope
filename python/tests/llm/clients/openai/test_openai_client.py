"""Tests for OpenAIClient using VCR.py for HTTP request recording/playback."""

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
    """VCR configuration for OpenAI API tests."""
    return {
        "record_mode": "once",
        "match_on": ["method", "uri", "body"],
        "filter_headers": ["authorization"],
        "filter_post_data_parameters": [],
    }


@pytest.fixture
def openai_client() -> llm.OpenAIClient:
    """Create an OpenAIClient instance with appropriate API key."""
    # Use real API key if available, otherwise dummy key for VCR tests
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY") or "dummy-key-for-vcr-tests"
    return llm.OpenAIClient(api_key=api_key)


@pytest.mark.vcr()
def test_call_simple_message(openai_client: llm.OpenAIClient) -> None:
    """Test basic call with a simple user message."""
    messages = [llm.messages.user("Hello, say 'Hi' back to me")]

    response = openai_client.call(
        model="gpt-4o-mini",
        messages=messages,
    )

    assert isinstance(response, llm.Response)

    assert response_snapshot_dict(response) == snapshot(
        {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "finish_reason": llm.FinishReason.END_TURN,
            "messages": [
                llm.UserMessage(content=[llm.Text(text="Hello, say 'Hi' back to me")]),
                llm.AssistantMessage(
                    content=[llm.Text(text="Hi! How can I assist you today?")]
                ),
            ],
            "content": [llm.Text(text="Hi! How can I assist you today?")],
            "texts": [llm.Text(text="Hi! How can I assist you today?")],
            "tool_calls": [],
            "thinkings": [],
        }
    )


@pytest.mark.vcr()
def test_call_with_system_message(openai_client: llm.OpenAIClient) -> None:
    """Test call with system and user messages."""
    messages = [
        llm.messages.system(
            "You are a cat who can only meow, and does not know anything about geography."
        ),
        llm.messages.user("What is the capital of France?"),
    ]

    response = openai_client.call(
        model="gpt-4o-mini",
        messages=messages,
    )

    assert isinstance(response, llm.Response)

    assert response_snapshot_dict(response) == snapshot(
        {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "finish_reason": llm.FinishReason.END_TURN,
            "messages": [
                llm.SystemMessage(
                    content=llm.Text(
                        text="You are a cat who can only meow, and does not know anything about geography."
                    )
                ),
                llm.UserMessage(
                    content=[llm.Text(text="What is the capital of France?")]
                ),
                llm.AssistantMessage(content=[llm.Text(text="Meow!")]),
            ],
            "content": [llm.Text(text="Meow!")],
            "texts": [llm.Text(text="Meow!")],
            "tool_calls": [],
            "thinkings": [],
        }
    )


@pytest.mark.vcr()
def test_call_with_turns(openai_client: llm.OpenAIClient) -> None:
    """Test basic call with a simple user message."""
    messages = [
        llm.messages.system("Be as concise as possible"),
        llm.messages.user("Recommend a book"),
        llm.messages.assistant("What genre would you like?"),
        llm.messages.user("Something about the fall of the Roman Empire"),
    ]

    response = openai_client.call(
        model="gpt-4o-mini",
        messages=messages,
    )

    assert isinstance(response, llm.Response)

    assert response_snapshot_dict(response) == snapshot(
        {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "finish_reason": llm.FinishReason.END_TURN,
            "messages": [
                llm.SystemMessage(content=llm.Text(text="Be as concise as possible")),
                llm.UserMessage(content=[llm.Text(text="Recommend a book")]),
                llm.AssistantMessage(
                    content=[llm.Text(text="What genre would you like?")]
                ),
                llm.UserMessage(
                    content=[
                        llm.Text(text="Something about the fall of the Roman Empire")
                    ]
                ),
                llm.AssistantMessage(
                    content=[
                        llm.Text(
                            text="I recommend \"The History of the Decline and Fall of the Roman Empire\" by Edward Gibbon. It's a classic work that examines the factors leading to the empire's collapse."
                        )
                    ]
                ),
            ],
            "content": [
                llm.Text(
                    text="I recommend \"The History of the Decline and Fall of the Roman Empire\" by Edward Gibbon. It's a classic work that examines the factors leading to the empire's collapse."
                )
            ],
            "texts": [
                llm.Text(
                    text="I recommend \"The History of the Decline and Fall of the Roman Empire\" by Edward Gibbon. It's a classic work that examines the factors leading to the empire's collapse."
                )
            ],
            "tool_calls": [],
            "thinkings": [],
        }
    )


@pytest.mark.vcr()
def test_stream_simple_message(openai_client: llm.OpenAIClient) -> None:
    """Test basic streaming with a simple user message."""
    messages = [llm.messages.user("Hi! Please greet me back.")]

    stream_response = openai_client.stream(
        model="gpt-4o-mini",
        messages=messages,
    )

    assert isinstance(stream_response, llm.responses.StreamResponse)
    for _ in stream_response.chunk_stream():
        ...

    assert stream_response_snapshot_dict(stream_response) == snapshot(
        {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "finish_reason": llm.FinishReason.END_TURN,
            "messages": [
                llm.UserMessage(content=[llm.Text(text="Hi! Please greet me back.")]),
                llm.AssistantMessage(
                    content=[
                        llm.Text(
                            text="Hello! I'm glad to hear from you. How can I assist you today?"
                        )
                    ]
                ),
            ],
            "content": [
                llm.Text(
                    text="Hello! I'm glad to hear from you. How can I assist you today?"
                )
            ],
            "texts": [
                llm.Text(
                    text="Hello! I'm glad to hear from you. How can I assist you today?"
                )
            ],
            "tool_calls": [],
            "thinkings": [],
            "consumed": True,
            "chunks": [
                llm.TextStartChunk(type="text_start_chunk"),
                llm.TextChunk(delta=""),
                llm.TextChunk(delta="Hello"),
                llm.TextChunk(delta="!"),
                llm.TextChunk(delta=" I'm"),
                llm.TextChunk(delta=" glad"),
                llm.TextChunk(delta=" to"),
                llm.TextChunk(delta=" hear"),
                llm.TextChunk(delta=" from"),
                llm.TextChunk(delta=" you"),
                llm.TextChunk(delta="."),
                llm.TextChunk(delta=" How"),
                llm.TextChunk(delta=" can"),
                llm.TextChunk(delta=" I"),
                llm.TextChunk(delta=" assist"),
                llm.TextChunk(delta=" you"),
                llm.TextChunk(delta=" today"),
                llm.TextChunk(delta="?"),
                llm.TextEndChunk(type="text_end_chunk"),
                llm.FinishReasonChunk(finish_reason=llm.FinishReason.END_TURN),
            ],
        }
    )
