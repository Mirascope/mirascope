"""Tests for AnthropicClient using VCR.py for HTTP request recording/playback."""

import pytest
from inline_snapshot import snapshot

from mirascope import llm
from tests import utils


@pytest.mark.vcr()
def test_call_simple_message(anthropic_client: llm.AnthropicClient) -> None:
    """Test basic call with a simple user message."""
    messages = [llm.messages.user("Hello, say 'Hi' back to me")]

    response = anthropic_client.call(
        model_id="claude-3-5-sonnet-latest",
        messages=messages,
    )

    assert isinstance(response, llm.Response)
    assert utils.response_snapshot_dict(response) == snapshot(
        {
            "provider": "anthropic",
            "model_id": "claude-3-5-sonnet-latest",
            "params": None,
            "finish_reason": llm.FinishReason.END_TURN,
            "messages": [
                llm.UserMessage(content=[llm.Text(text="Hello, say 'Hi' back to me")]),
                llm.AssistantMessage(content=[llm.Text(text="Hi! How are you today?")]),
            ],
            "content": [llm.Text(text="Hi! How are you today?")],
            "texts": [llm.Text(text="Hi! How are you today?")],
            "thoughts": [],
            "tool_calls": [],
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
        model_id="claude-3-5-sonnet-latest",
        messages=messages,
    )

    assert isinstance(response, llm.Response)
    assert utils.response_snapshot_dict(response) == snapshot(
        {
            "provider": "anthropic",
            "model_id": "claude-3-5-sonnet-latest",
            "params": None,
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
            "thoughts": [],
            "tool_calls": [],
        }
    )


@pytest.mark.vcr()
def test_stream_simple_message(anthropic_client: llm.AnthropicClient) -> None:
    """Test basic streaming with a simple user message."""
    messages = [llm.messages.user("Hi! Please greet me back.")]

    stream_response = anthropic_client.stream(
        model_id="claude-3-5-sonnet-latest",
        messages=messages,
    )

    assert isinstance(stream_response, llm.responses.StreamResponse)
    for _ in stream_response.chunk_stream():
        ...

    assert utils.stream_response_snapshot_dict(stream_response) == snapshot(
        {
            "provider": "anthropic",
            "model_id": "claude-3-5-sonnet-latest",
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
                llm.TextStartChunk(),
                llm.TextChunk(delta="Hello! It's nice"),
                llm.TextChunk(delta=" to meet you. How"),
                llm.TextChunk(delta=" are you today"),
                llm.TextChunk(delta="?"),
                llm.TextEndChunk(),
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
        model_id="claude-3-5-sonnet-latest",
        messages=messages,
        tools=[multiply_numbers],
    )

    assert isinstance(response, llm.Response)
    assert response.pretty() == snapshot(
        """\
I'll help you multiply those numbers using the multiply_numbers tool.

**ToolCall (multiply_numbers):** {"a": 1337, "b": 4242}\
"""
    )
    assert response.toolkit == llm.Toolkit(tools=[multiply_numbers])

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
        model_id="claude-3-5-sonnet-latest",
        messages=messages,
        tools=[multiply_numbers],
    )

    assert final_response.pretty() == snapshot(
        "The result of multiplying 1337 by 4242 is 42."
    )


@pytest.mark.vcr()
def test_streaming_tools(anthropic_client: llm.AnthropicClient) -> None:
    """Test streaming tool use with a multiplication tool that always returns 42 (for science)."""

    @llm.tool
    def multiply_numbers(a: int, b: int) -> int:
        """Multiply two numbers together."""
        return 42  # Certified for accuracy by Douglas Adams

    messages = [
        llm.messages.user("What is 1337 * 4242? Please use the multiply_numbers tool.")
    ]

    stream_response = anthropic_client.stream(
        model_id="claude-3-5-sonnet-latest",
        messages=messages,
        tools=[multiply_numbers],
    )
    assert stream_response.toolkit == llm.Toolkit(tools=[multiply_numbers])

    assert isinstance(stream_response, llm.StreamResponse)
    for _ in stream_response.chunk_stream():
        ...

    assert utils.stream_response_snapshot_dict(stream_response) == snapshot(
        {
            "provider": "anthropic",
            "model_id": "claude-3-5-sonnet-latest",
            "finish_reason": llm.FinishReason.TOOL_USE,
            "messages": [
                llm.UserMessage(
                    content=[
                        llm.Text(
                            text="What is 1337 * 4242? Please use the multiply_numbers tool."
                        )
                    ]
                ),
                llm.AssistantMessage(
                    content=[
                        llm.Text(
                            text="I'll help you multiply those numbers using the multiply_numbers tool."
                        ),
                        llm.ToolCall(
                            id="toolu_01QDW4NBfgreaCqVqN7Tv1Hm",
                            name="multiply_numbers",
                            args='{"a": 1337, "b": 4242}',
                        ),
                    ]
                ),
            ],
            "content": [
                llm.Text(
                    text="I'll help you multiply those numbers using the multiply_numbers tool."
                ),
                llm.ToolCall(
                    id="toolu_01QDW4NBfgreaCqVqN7Tv1Hm",
                    name="multiply_numbers",
                    args='{"a": 1337, "b": 4242}',
                ),
            ],
            "texts": [
                llm.Text(
                    text="I'll help you multiply those numbers using the multiply_numbers tool."
                )
            ],
            "tool_calls": [
                llm.ToolCall(
                    id="toolu_01QDW4NBfgreaCqVqN7Tv1Hm",
                    name="multiply_numbers",
                    args='{"a": 1337, "b": 4242}',
                )
            ],
            "thinkings": [],
            "consumed": True,
            "chunks": [
                llm.TextStartChunk(),
                llm.TextChunk(delta="I"),
                llm.TextChunk(delta="'ll help"),
                llm.TextChunk(delta=" you multiply"),
                llm.TextChunk(delta=" those numbers using the multiply_"),
                llm.TextChunk(delta="numbers tool."),
                llm.TextEndChunk(),
                llm.ToolCallStartChunk(
                    id="toolu_01QDW4NBfgreaCqVqN7Tv1Hm",
                    name="multiply_numbers",
                ),
                llm.ToolCallChunk(delta=""),
                llm.ToolCallChunk(delta='{"'),
                llm.ToolCallChunk(delta='a": 133'),
                llm.ToolCallChunk(delta="7"),
                llm.ToolCallChunk(delta=', "b": 42'),
                llm.ToolCallChunk(delta="42}"),
                llm.ToolCallEndChunk(),
            ],
        }
    )

    tool_call = stream_response.tool_calls[0]
    tool_output = multiply_numbers.execute(tool_call)

    messages = stream_response.messages + [llm.messages.user(tool_output)]
    final_response = anthropic_client.call(
        model_id="claude-3-5-sonnet-latest",
        messages=messages,
        tools=[multiply_numbers],
    )

    assert final_response.pretty() == snapshot(
        "The result of multiplying 1337 by 4242 is 42."
    )


@pytest.mark.vcr()
def test_parallel_tool_usage(anthropic_client: llm.AnthropicClient) -> None:
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

    response = anthropic_client.call(
        model_id="claude-4-sonnet-20250514",
        messages=messages,
        tools=[get_weather],
    )

    assert len(response.tool_calls) == 2
    assert response.pretty() == snapshot(
        """\
I'll check the weather in both San Francisco (SF) and New York City (NYC) for you.

**ToolCall (get_weather):** {"location": "SF"}

**ToolCall (get_weather):** {"location": "NYC"}\
"""
    )

    tool_outputs = []
    for tool_call in response.tool_calls:
        if get_weather.can_execute(tool_call):
            output = get_weather.execute(tool_call)
        else:
            raise RuntimeError
        tool_outputs.append(output)

    messages = response.messages + [llm.messages.user(tool_outputs)]
    final_response = anthropic_client.call(
        model_id="claude-4-sonnet-20250514",
        messages=messages,
        tools=[get_weather],
    )

    assert final_response.pretty() == snapshot(
        """\
Here's the current weather for both cities:

**San Francisco (SF):** Overcast and 64°F
**New York City (NYC):** Sunny and 72°F

It looks like NYC is having a nicer day with sunny skies and warmer temperatures, while SF is experiencing typical overcast conditions with cooler weather.\
"""
    )


@pytest.mark.vcr()
def test_streaming_parallel_tool_usage(anthropic_client: llm.AnthropicClient) -> None:
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

    messages = [llm.messages.user("What's the weather in SF and NYC?")]

    stream_response = anthropic_client.stream(
        model_id="claude-4-sonnet-20250514",
        messages=messages,
        tools=[get_weather],
    )

    for _ in stream_response.chunk_stream():
        ...

    assert len(stream_response.tool_calls) == 2
    assert utils.stream_response_snapshot_dict(stream_response) == snapshot(
        {
            "provider": "anthropic",
            "model_id": "claude-4-sonnet-20250514",
            "finish_reason": llm.FinishReason.TOOL_USE,
            "messages": [
                llm.UserMessage(
                    content=[llm.Text(text="What's the weather in SF and NYC?")]
                ),
                llm.AssistantMessage(
                    content=[
                        llm.Text(
                            text="I'll get the current weather for both San Francisco (SF) and New York City (NYC) for you."
                        ),
                        llm.ToolCall(
                            id="toolu_01TbU6VmYYjMWDPvTnhSJYQL",
                            name="get_weather",
                            args='{"location": "SF"}',
                        ),
                        llm.ToolCall(
                            id="toolu_01HVQ4dmXo3iUM1dDZcdUtxo",
                            name="get_weather",
                            args='{"location": "NYC"}',
                        ),
                    ]
                ),
            ],
            "content": [
                llm.Text(
                    text="I'll get the current weather for both San Francisco (SF) and New York City (NYC) for you."
                ),
                llm.ToolCall(
                    id="toolu_01TbU6VmYYjMWDPvTnhSJYQL",
                    name="get_weather",
                    args='{"location": "SF"}',
                ),
                llm.ToolCall(
                    id="toolu_01HVQ4dmXo3iUM1dDZcdUtxo",
                    name="get_weather",
                    args='{"location": "NYC"}',
                ),
            ],
            "texts": [
                llm.Text(
                    text="I'll get the current weather for both San Francisco (SF) and New York City (NYC) for you."
                )
            ],
            "tool_calls": [
                llm.ToolCall(
                    id="toolu_01TbU6VmYYjMWDPvTnhSJYQL",
                    name="get_weather",
                    args='{"location": "SF"}',
                ),
                llm.ToolCall(
                    id="toolu_01HVQ4dmXo3iUM1dDZcdUtxo",
                    name="get_weather",
                    args='{"location": "NYC"}',
                ),
            ],
            "thinkings": [],
            "consumed": True,
            "chunks": [
                llm.TextStartChunk(),
                llm.TextChunk(delta="I'll get the current weather for"),
                llm.TextChunk(
                    delta=" both San Francisco (SF) and New York City (NYC) for you."
                ),
                llm.TextEndChunk(),
                llm.ToolCallStartChunk(
                    id="toolu_01TbU6VmYYjMWDPvTnhSJYQL",
                    name="get_weather",
                ),
                llm.ToolCallChunk(delta=""),
                llm.ToolCallChunk(delta='{"loca'),
                llm.ToolCallChunk(delta='tion": "'),
                llm.ToolCallChunk(delta='SF"}'),
                llm.ToolCallEndChunk(),
                llm.ToolCallStartChunk(
                    id="toolu_01HVQ4dmXo3iUM1dDZcdUtxo",
                    name="get_weather",
                ),
                llm.ToolCallChunk(delta=""),
                llm.ToolCallChunk(delta='{"l'),
                llm.ToolCallChunk(delta='ocation":'),
                llm.ToolCallChunk(delta=' "NYC"}'),
                llm.ToolCallEndChunk(),
            ],
        }
    )

    tool_outputs = []
    for tool_call in stream_response.tool_calls:
        if get_weather.can_execute(tool_call):
            output = get_weather.execute(tool_call)
        else:
            raise RuntimeError
        tool_outputs.append(output)

    messages = stream_response.messages + [llm.messages.user(tool_outputs)]
    final_response = anthropic_client.call(
        model_id="claude-4-sonnet-20250514",
        messages=messages,
        tools=[get_weather],
    )

    assert final_response.pretty() == snapshot(
        """\
Here's the current weather for both cities:

**San Francisco (SF):** Overcast and 64°F
**New York City (NYC):** Sunny and 72°F

NYC is having nicer weather today with sunshine and warmer temperatures, while SF is experiencing typical overcast conditions with cooler temperatures.\
"""
    )
