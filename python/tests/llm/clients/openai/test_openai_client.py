"""Tests for OpenAIClient using VCR.py for HTTP request recording/playback."""

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


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration for OpenAI API tests."""
    return {
        "record_mode": "once",
        "match_on": ["method", "uri", "body"],
        "filter_headers": ["authorization"],
        "filter_post_data_parameters": [],
    }


@pytest.fixture
def openai_client():
    """Create an OpenAIClient instance with appropriate API key."""
    # Use real API key if available, otherwise dummy key for VCR tests
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY") or "dummy-key-for-vcr-tests"
    return llm.clients.OpenAIClient(api_key=api_key)


@pytest.mark.vcr()
def test_call_simple_message(openai_client):
    """Test basic call with a simple user message."""
    messages = [llm.messages.user("Hello, say 'Hi' back to me")]

    response = openai_client.call(
        model="gpt-4o-mini",
        messages=messages,
    )

    assert isinstance(response, llm.responses.Response)

    response.__dict__.pop("raw")
    assert response.__dict__ == snapshot(
        {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "finish_reason": FinishReason.END_TURN,
            "messages": [
                UserMessage(content=[Text(text="Hello, say 'Hi' back to me")]),
                AssistantMessage(
                    content=[Text(text="Hi! How can I assist you today?")]
                ),
            ],
            "content": [Text(text="Hi! How can I assist you today?")],
            "texts": [Text(text="Hi! How can I assist you today?")],
            "tool_calls": [],
            "thinkings": [],
        }
    )


@pytest.mark.vcr()
def test_call_with_system_message(openai_client):
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

    assert isinstance(response, llm.responses.Response)

    response.__dict__.pop("raw")
    assert response.__dict__ == snapshot(
        {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "finish_reason": FinishReason.END_TURN,
            "messages": [
                SystemMessage(
                    content=Text(
                        text="You are a cat who can only meow, and does not know anything about geography."
                    )
                ),
                UserMessage(content=[Text(text="What is the capital of France?")]),
                AssistantMessage(content=[Text(text="Meow!")]),
            ],
            "content": [Text(text="Meow!")],
            "texts": [Text(text="Meow!")],
            "tool_calls": [],
            "thinkings": [],
        }
    )


@pytest.mark.vcr()
def test_call_with_turns(openai_client):
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

    assert isinstance(response, llm.responses.Response)

    response.__dict__.pop("raw")
    assert response.__dict__ == snapshot(
        {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "finish_reason": FinishReason.END_TURN,
            "messages": [
                SystemMessage(content=Text(text="Be as concise as possible")),
                UserMessage(content=[Text(text="Recommend a book")]),
                AssistantMessage(content=[Text(text="What genre would you like?")]),
                UserMessage(
                    content=[Text(text="Something about the fall of the Roman Empire")]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="I recommend \"The History of the Decline and Fall of the Roman Empire\" by Edward Gibbon. It's a classic work that examines the factors leading to the empire's collapse."
                        )
                    ]
                ),
            ],
            "content": [
                Text(
                    text="I recommend \"The History of the Decline and Fall of the Roman Empire\" by Edward Gibbon. It's a classic work that examines the factors leading to the empire's collapse."
                )
            ],
            "texts": [
                Text(
                    text="I recommend \"The History of the Decline and Fall of the Roman Empire\" by Edward Gibbon. It's a classic work that examines the factors leading to the empire's collapse."
                )
            ],
            "tool_calls": [],
            "thinkings": [],
        }
    )
