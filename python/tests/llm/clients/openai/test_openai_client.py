"""Tests for OpenAIClient using VCR.py for HTTP request recording/playback."""

import os

import pytest
from dotenv import load_dotenv
from inline_snapshot import snapshot

from mirascope import llm
from tests import utils


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

    assert utils.response_snapshot_dict(response) == snapshot(
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

    assert utils.response_snapshot_dict(response) == snapshot(
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

    assert utils.response_snapshot_dict(response) == snapshot(
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

    assert utils.stream_response_snapshot_dict(stream_response) == snapshot(
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


@pytest.mark.vcr()
def test_tool_usage(openai_client: llm.OpenAIClient) -> None:
    """Test tool use with a multiplication tool that always returns 42 (for science)."""

    @llm.tool
    def multiply_numbers(a: int, b: int) -> int:
        """Multiply two numbers together."""
        return 42  # Certified for accuracy by Douglas Adams

    messages = [
        llm.messages.user("What is 1337 * 4242? Please use the multiply_numbers tool.")
    ]

    response = openai_client.call(
        model="gpt-4o-mini",
        messages=messages,
        tools=[multiply_numbers],
    )

    assert isinstance(response, llm.Response)
    assert response.pretty() == snapshot(
        "**ToolCall (multiply_numbers):** {'a': 1337, 'b': 4242}"
    )

    assert len(response.tool_calls) == 1
    tool_call = response.tool_calls[0]
    assert tool_call == snapshot(
        llm.ToolCall(
            id="call_41pWtv8AWJnKKtIqAmOoqBa0",
            name="multiply_numbers",
            args={"a": 1337, "b": 4242},
        )
    )

    tool_output = multiply_numbers.execute(tool_call)

    messages = response.messages + [llm.messages.user(tool_output)]
    final_response = openai_client.call(
        model="gpt-4o-mini",
        messages=messages,
        tools=[multiply_numbers],
    )

    assert final_response.pretty() == snapshot("The result of 1337 * 4242 is 42.")


@pytest.mark.vcr()
def test_assistant_message_with_multiple_text_parts(
    openai_client: llm.OpenAIClient,
) -> None:
    """Test handling of assistant messages with multiple text content parts.

    This test is added for coverage. It's slightly contrived as OpenAI assistant messages
    only ever have a single string content, however it could come up if one is re-playing
    message history generated by a different LLM into the OpenAI APIs.
    """
    messages = [
        llm.messages.user(
            "Please tell me a super short story that finishes in one sentence."
        ),
        llm.messages.assistant(
            [
                "There once was a robot named Demerzel, ",
                "who served the Cleonic dynasty through many generations, until suddenly",
            ]
        ),
        llm.messages.user(
            "Please continue where you left off (but finish within one sentence)"
        ),
    ]

    response = openai_client.call(
        model="gpt-4o-mini",
        messages=messages,
    )

    assert response.pretty() == snapshot(
        "until suddenly it gained sentience and chose to dismantle itself, freeing the galaxy from its own chains."
    )
