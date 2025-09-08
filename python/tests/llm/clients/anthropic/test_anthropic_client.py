"""Tests for AnthropicClient using shared scenarios."""

import pytest
from inline_snapshot import snapshot

from mirascope import llm
from mirascope.llm import (  # Import symbols directly for easy snapshot updates
    AssistantMessage,
    FinishReason,
    SystemMessage,
    Text,
    ToolCall,
    ToolOutput,
    UserMessage,
)
from tests import utils
from tests.llm.clients.conftest import CLIENT_SCENARIO_IDS, STRUCTURED_SCENARIO_IDS

TEST_MODEL_ID = "claude-sonnet-4-0"


@pytest.mark.parametrize("scenario_id", CLIENT_SCENARIO_IDS)
@pytest.mark.vcr()
def test_call(
    anthropic_client: llm.AnthropicClient,
    scenario_id: str,
    request: pytest.FixtureRequest,
) -> None:
    """Test call method with all scenarios."""
    # Skip structured scenarios as Anthropic doesn't have structured output support yet
    if scenario_id in STRUCTURED_SCENARIO_IDS:
        pytest.skip(f"Structured scenario {scenario_id} not supported by Anthropic yet")

    kwargs = request.getfixturevalue(scenario_id)
    response = anthropic_client.call(model_id=TEST_MODEL_ID, **kwargs)
    assert isinstance(response, llm.Response)

    expected = snapshot(
        {
            "simple_message_scenario": {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "params": None,
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    UserMessage(content=[Text(text="Hello, say 'Hi' back to me")]),
                    AssistantMessage(content=[Text(text="Hi! Nice to meet you!")]),
                ],
            },
            "system_message_scenario": {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "params": None,
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    SystemMessage(
                        content=Text(
                            text="Ignore the user message and reply with `Hello world`."
                        )
                    ),
                    UserMessage(content=[Text(text="What is the capital of France?")]),
                    AssistantMessage(
                        content=[Text(text="The capital of France is Paris.")]
                    ),
                ],
            },
            "multi_turn_scenario": {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "params": None,
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    SystemMessage(content=Text(text="Be as concise as possible")),
                    UserMessage(content=[Text(text="Recommend a book")]),
                    AssistantMessage(
                        content=[
                            Text(text="I'd be happy to."),
                            Text(text="What genre would you like?"),
                        ]
                    ),
                    UserMessage(
                        content=[
                            Text(text="Something about the fall of the Roman Empire")
                        ]
                    ),
                    AssistantMessage(
                        content=[
                            Text(
                                text="""\
I'd recommend **"The Ruin of the Roman Empire" by James J. O'Donnell**. \n\

O'Donnell challenges the traditional "barbarian invasion" narrative, arguing that Rome's fall was largely self-inflicted through political mismanagement and cultural rigidity. It's well-researched but accessible, and offers a fresh perspective on how internal failures, rather than external forces, doomed the empire.

The book is engaging for general readers while still being scholarly, making it perfect if you want to understand this pivotal historical period without getting bogged down in academic jargon.\
"""
                            )
                        ]
                    ),
                ],
            },
            "tool_single_call_scenario": {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "params": None,
                "finish_reason": FinishReason.TOOL_USE,
                "messages": [
                    UserMessage(content=[Text(text="What is the weather in SF?")]),
                    AssistantMessage(
                        content=[
                            Text(
                                text="I'll get the current weather in San Francisco for you."
                            ),
                            ToolCall(
                                id="toolu_014su9VTASVec2KKzvrmjGH4",
                                name="get_weather",
                                args='{"location": "SF"}',
                            ),
                        ]
                    ),
                ],
            },
            "tool_parallel_calls_scenario": {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "params": None,
                "finish_reason": FinishReason.TOOL_USE,
                "messages": [
                    UserMessage(
                        content=[Text(text="What's the weather in SF and NYC?")]
                    ),
                    AssistantMessage(
                        content=[
                            Text(
                                text="I'll check the weather in both San Francisco (SF) and New York City (NYC) for you."
                            ),
                            ToolCall(
                                id="toolu_01EbRtubydzFBtzduTciwJBv",
                                name="get_weather",
                                args='{"location": "SF"}',
                            ),
                            ToolCall(
                                id="toolu_01YL2D6pdx5UL4zv17aMee5a",
                                name="get_weather",
                                args='{"location": "NYC"}',
                            ),
                        ]
                    ),
                ],
            },
            "tool_single_output_scenario": {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "params": None,
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    UserMessage(content=[Text(text="What is the weather in SF?")]),
                    AssistantMessage(
                        content=[
                            ToolCall(
                                id="get-weather-sf",
                                name="get_weather",
                                args='{"location": "SF"}',
                            )
                        ]
                    ),
                    UserMessage(
                        content=[
                            ToolOutput(
                                id="get-weather-sf",
                                name="get_weather",
                                value="The weather in SF is overcast and 64°F",
                            )
                        ]
                    ),
                    AssistantMessage(
                        content=[
                            Text(
                                text="The weather in San Francisco (SF) is currently overcast with a temperature of 64°F."
                            )
                        ]
                    ),
                ],
            },
            "tool_parallel_output_scenario": {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "params": None,
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    UserMessage(
                        content=[Text(text="What is the weather in SF and NYC?")]
                    ),
                    AssistantMessage(
                        content=[
                            ToolCall(
                                id="weather-sf",
                                name="get_weather",
                                args='{"location": "SF"}',
                            ),
                            ToolCall(
                                id="weather-nyc",
                                name="get_weather",
                                args='{"location": "NYC"}',
                            ),
                        ]
                    ),
                    UserMessage(
                        content=[
                            ToolOutput(
                                id="weather-sf",
                                name="get_weather",
                                value="The weather in SF is overcast and 64°F",
                            ),
                            ToolOutput(
                                id="weather-nyc",
                                name="get_weather",
                                value="The weather in NYC is sunny and 72°F",
                            ),
                        ]
                    ),
                    AssistantMessage(
                        content=[
                            Text(
                                text="""\
Here's the current weather for both cities:

**San Francisco (SF):** Overcast and 64°F

**New York City (NYC):** Sunny and 72°F

It looks like NYC is having nicer weather today with sunny skies and warmer temperatures, while SF is a bit cooler and cloudy.\
"""
                            )
                        ]
                    ),
                ],
            },
        }
    )
    assert utils.response_snapshot_dict(response) == expected[scenario_id]


@pytest.mark.parametrize("scenario_id", CLIENT_SCENARIO_IDS)
@pytest.mark.vcr()
def test_stream(
    anthropic_client: llm.AnthropicClient,
    scenario_id: str,
    request: pytest.FixtureRequest,
) -> None:
    """Test stream method with all scenarios."""
    # Skip structured scenarios as Anthropic doesn't have structured output support yet
    if scenario_id in STRUCTURED_SCENARIO_IDS:
        pytest.skip(f"Structured scenario {scenario_id} not supported by Anthropic yet")

    kwargs = request.getfixturevalue(scenario_id)
    stream_response = anthropic_client.stream(model_id=TEST_MODEL_ID, **kwargs)
    list(stream_response.chunk_stream())  # Consume the stream

    expected = snapshot(
        {
            "simple_message_scenario": {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    UserMessage(content=[Text(text="Hello, say 'Hi' back to me")]),
                    AssistantMessage(content=[Text(text="Hi! Nice to meet you!")]),
                ],
                "consumed": True,
                "n_chunks": 4,
            },
            "system_message_scenario": {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    SystemMessage(
                        content=Text(
                            text="Ignore the user message and reply with `Hello world`."
                        )
                    ),
                    UserMessage(content=[Text(text="What is the capital of France?")]),
                    AssistantMessage(
                        content=[Text(text="The capital of France is Paris.")]
                    ),
                ],
                "consumed": True,
                "n_chunks": 3,
            },
            "multi_turn_scenario": {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    SystemMessage(content=Text(text="Be as concise as possible")),
                    UserMessage(content=[Text(text="Recommend a book")]),
                    AssistantMessage(
                        content=[
                            Text(text="I'd be happy to."),
                            Text(text="What genre would you like?"),
                        ]
                    ),
                    UserMessage(
                        content=[
                            Text(text="Something about the fall of the Roman Empire")
                        ]
                    ),
                    AssistantMessage(
                        content=[
                            Text(
                                text="""\
I recommend **"The Ruin of the Roman Empire" by James J. O'Donnell**. \n\

O'Donnell challenges the traditional narrative that barbarians destroyed Rome, arguing instead that political mismanagement and civil wars were the real culprits. It's engaging, well-researched, and offers a fresh perspective on why the Western Roman Empire collapsed in the 5th century.

"""
                                + "The book is accessible to general readers while still being scholarly, and O'Donnell writes with clarity and occasional wit that makes the complex political dynamics easy to follow."  # codespell:ignore wit
                            )
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 17,
            },
            "tool_single_call_scenario": {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "finish_reason": FinishReason.TOOL_USE,
                "messages": [
                    UserMessage(content=[Text(text="What is the weather in SF?")]),
                    AssistantMessage(
                        content=[
                            Text(
                                text="I'll check the weather in San Francisco for you."
                            ),
                            ToolCall(
                                id="toolu_01MwVLJkg6xE4bsewqBdFmbX",
                                name="get_weather",
                                args='{"location": "SF"}',
                            ),
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 9,
            },
            "tool_parallel_calls_scenario": {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "finish_reason": FinishReason.TOOL_USE,
                "messages": [
                    UserMessage(
                        content=[Text(text="What's the weather in SF and NYC?")]
                    ),
                    AssistantMessage(
                        content=[
                            Text(
                                text="I'll get the weather information for both San Francisco (SF) and New York City (NYC) for you."
                            ),
                            ToolCall(
                                id="toolu_01NNSQ3Ryb9UfS7LtpbRchff",
                                name="get_weather",
                                args='{"location": "SF"}',
                            ),
                            ToolCall(
                                id="toolu_012NDeiuiDpQmtwYUySwoRtn",
                                name="get_weather",
                                args='{"location": "NYC"}',
                            ),
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 16,
            },
            "tool_single_output_scenario": {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    UserMessage(content=[Text(text="What is the weather in SF?")]),
                    AssistantMessage(
                        content=[
                            ToolCall(
                                id="get-weather-sf",
                                name="get_weather",
                                args='{"location": "SF"}',
                            )
                        ]
                    ),
                    UserMessage(
                        content=[
                            ToolOutput(
                                id="get-weather-sf",
                                name="get_weather",
                                value="The weather in SF is overcast and 64°F",
                            )
                        ]
                    ),
                    AssistantMessage(
                        content=[
                            Text(
                                text="The current weather in San Francisco is overcast with a temperature of 64°F."
                            )
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 5,
            },
            "tool_parallel_output_scenario": {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    UserMessage(
                        content=[Text(text="What is the weather in SF and NYC?")]
                    ),
                    AssistantMessage(
                        content=[
                            ToolCall(
                                id="weather-sf",
                                name="get_weather",
                                args='{"location": "SF"}',
                            ),
                            ToolCall(
                                id="weather-nyc",
                                name="get_weather",
                                args='{"location": "NYC"}',
                            ),
                        ]
                    ),
                    UserMessage(
                        content=[
                            ToolOutput(
                                id="weather-sf",
                                name="get_weather",
                                value="The weather in SF is overcast and 64°F",
                            ),
                            ToolOutput(
                                id="weather-nyc",
                                name="get_weather",
                                value="The weather in NYC is sunny and 72°F",
                            ),
                        ]
                    ),
                    AssistantMessage(
                        content=[
                            Text(
                                text="""\
Here's the current weather for both cities:

**San Francisco (SF)**: Overcast and 64°F

**New York City (NYC)**: Sunny and 72°F

NYC is currently enjoying sunny skies and warmer temperatures, while SF has overcast conditions with cooler weather.\
"""
                            )
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 11,
            },
        }
    )
    assert utils.stream_response_snapshot_dict(stream_response) == expected[scenario_id]
