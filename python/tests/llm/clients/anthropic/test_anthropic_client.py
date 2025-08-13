"""Tests for AnthropicClient using VCR.py for HTTP request recording/playback."""

import inspect
import os

import pytest
from dotenv import load_dotenv
from inline_snapshot import snapshot

from mirascope import llm
from tests import utils


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
    assert utils.response_snapshot_dict(response) == snapshot(
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
    assert utils.response_snapshot_dict(response) == snapshot(
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

    assert utils.stream_response_snapshot_dict(stream_response) == snapshot(
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


@pytest.mark.vcr()
def test_tool_usage(anthropic_client: llm.AnthropicClient) -> None:
    """Test tool use with a multiplication tool that always returns 42 (for science)."""

    @llm.tool
    def multiply_numbers(a: int, b: int) -> int:
        """Multiply two numbers together."""
        return 42  # Certified for accuracy by Douglas Adams

    messages = [
        llm.messages.user("What is 1337 * 4242? Please use the multiply_numbers tool.")
    ]

    response = anthropic_client.call(
        model="claude-3-5-sonnet-latest",
        messages=messages,
        tools=[multiply_numbers],
    )

    assert isinstance(response, llm.Response)
    assert response.pretty() == snapshot(
        inspect.cleandoc("""\
        I'll help you multiply those numbers using the multiply_numbers tool.

        **ToolCall (multiply_numbers):** {"a": 1337, "b": 4242}
        """)
    )

    assert len(response.tool_calls) == 1
    tool_call = response.tool_calls[0]
    assert tool_call == snapshot(
        llm.ToolCall(
            id="toolu_01EcyDhLAzjUwsiXJrJieL1p",
            name="multiply_numbers",
            args='{"a": 1337, "b": 4242}',
        )
    )

    tool_output = multiply_numbers.execute(tool_call)

    messages = response.messages + [llm.messages.user(tool_output)]
    final_response = anthropic_client.call(
        model="claude-3-5-sonnet-latest",
        messages=messages,
        tools=[multiply_numbers],
    )

    assert final_response.pretty() == snapshot(
        "The result of multiplying 1337 by 4242 is 42."
    )
