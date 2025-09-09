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
from tests.llm.clients.conftest import (
    CLIENT_SCENARIO_IDS,
    FORMATTING_MODES,
    STRUCTURED_SCENARIO_IDS,
)

TEST_MODEL_ID = "claude-sonnet-4-0"


@pytest.mark.parametrize("scenario_id", CLIENT_SCENARIO_IDS)
@pytest.mark.vcr()
def test_call(
    anthropic_client: llm.AnthropicClient,
    scenario_id: str,
    request: pytest.FixtureRequest,
) -> None:
    """Test call method with all scenarios."""

    kwargs = request.getfixturevalue(scenario_id)
    response = anthropic_client.call(model_id=TEST_MODEL_ID, **kwargs)

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
            "structured_output_basic_scenario": {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "params": None,
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    SystemMessage(
                        content=Text(
                            text="""\
When you are ready to respond to the user, call the __mirascope_formatted_output_tool__ tool to output a structured response.
Do NOT output any text in addition to the tool call.\
"""
                        )
                    ),
                    UserMessage(
                        content=[Text(text="Recommend a single fantasy book.")]
                    ),
                    AssistantMessage(
                        content=[
                            Text(
                                text='{"title": "The Name of the Wind", "author": "Patrick Rothfuss", "vibe": "mysterious!"}'
                            )
                        ]
                    ),
                ],
            },
            "structured_output_should_call_tool_scenario": {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "params": None,
                "finish_reason": FinishReason.TOOL_USE,
                "messages": [
                    SystemMessage(
                        content=Text(
                            text="""\
When you are ready to respond to the user, call the __mirascope_formatted_output_tool__ tool to output a structured response.
Do NOT output any text in addition to the tool call.\
"""
                        )
                    ),
                    UserMessage(
                        content=[
                            Text(text="Recommend a single fantasy book in the library.")
                        ]
                    ),
                    AssistantMessage(
                        content=[
                            ToolCall(
                                id="toolu_013AHZ4xpW1gcYYXbTVYh1xT",
                                name="available_books",
                                args="{}",
                            )
                        ]
                    ),
                ],
            },
            "structured_output_uses_tool_output_scenario": {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "params": None,
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    SystemMessage(
                        content=Text(
                            text="""\
When you are ready to respond to the user, call the __mirascope_formatted_output_tool__ tool to output a structured response.
Do NOT output any text in addition to the tool call.\
"""
                        )
                    ),
                    UserMessage(
                        content=[
                            Text(text="Recommend a single fantasy book in the library.")
                        ]
                    ),
                    AssistantMessage(
                        content=[
                            ToolCall(id="call_123", name="available_books", args="{}")
                        ]
                    ),
                    UserMessage(
                        content=[
                            ToolOutput(
                                id="call_123",
                                name="available_books",
                                value=[
                                    "Wild Seed by Octavia Butler",
                                    "The Long Way to a Small Angry Planet by Becky Chambers",
                                    "Emergent Strategy by adrianne maree brown",
                                ],
                            )
                        ]
                    ),
                    AssistantMessage(
                        content=[
                            Text(
                                text='{"title": "Wild Seed", "author": "Octavia Butler", "vibe": "mysterious!"}'
                            )
                        ]
                    ),
                ],
            },
            "structured_output_with_formatting_instructions_scenario": {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "params": None,
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    SystemMessage(
                        content=Text(
                            text="""\
Pretty please output a book recommendation in JSON form.
It should have the format {title: str, author: str, vibe: str}.
Be super vibe-y with the vibe and make sure EVERYTHING IS CAPS to convey
the STRENGTH OF YOUR RECOMMENDATION!\
"""
                        )
                    ),
                    UserMessage(
                        content=[Text(text="Recommend a single fantasy book.")]
                    ),
                    AssistantMessage(
                        content=[
                            Text(
                                text='{"title": "THE NAME OF THE WIND", "author": "PATRICK ROTHFUSS", "vibe": "INTRIGUING"}'
                            )
                        ]
                    ),
                ],
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario": {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "params": None,
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    SystemMessage(
                        content=Text(
                            text="""\
You are a depressive LLM that only recommends sad books.
Pretty please output a book recommendation in JSON form.
It should have the format {title: str, author: str, vibe: str}.
Be super vibe-y with the vibe and make sure EVERYTHING IS CAPS to convey
the STRENGTH OF YOUR RECOMMENDATION!\
"""
                        )
                    ),
                    UserMessage(
                        content=[Text(text="Recommend a single fantasy book.")]
                    ),
                    AssistantMessage(
                        content=[
                            Text(
                                text='{"title": "THE BROKEN EARTH TRILOGY", "author": "N.K. JEMISIN", "vibe": "soul_searching"}'
                            )
                        ]
                    ),
                ],
            },
            "structured_output_with_nested_models_scenario": {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "params": None,
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    SystemMessage(
                        content=Text(
                            text="""\
When you are ready to respond to the user, call the __mirascope_formatted_output_tool__ tool to output a structured response.
Do NOT output any text in addition to the tool call.\
"""
                        )
                    ),
                    UserMessage(content=[Text(text="Tell me about a book series.")]),
                    AssistantMessage(
                        content=[
                            Text(
                                text='{"series_name": "The Expanse", "author": "James S.A. Corey", "book_count": 9, "books": [{"title": "Leviathan Wakes", "author": "James S.A. Corey", "vibe": "mysterious!"}, {"title": "Caliban\'s War", "author": "James S.A. Corey", "vibe": "intruiging!"}, {"title": "Abaddon\'s Gate", "author": "James S.A. Corey", "vibe": "mysterious!"}, {"title": "Cibola Burn", "author": "James S.A. Corey", "vibe": "soul_searching!"}, {"title": "Nemesis Games", "author": "James S.A. Corey", "vibe": "euphoric!"}, {"title": "Babylon\'s Ashes", "author": "James S.A. Corey", "vibe": "intruiging!"}, {"title": "Persepolis Rising", "author": "James S.A. Corey", "vibe": "mysterious!"}, {"title": "Tiamat\'s Wrath", "author": "James S.A. Corey", "vibe": "euphoric!"}, {"title": "Leviathan Falls", "author": "James S.A. Corey", "vibe": "soul_searching!"}]}'
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
            "structured_output_basic_scenario": {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    SystemMessage(
                        content=Text(
                            text="""\
When you are ready to respond to the user, call the __mirascope_formatted_output_tool__ tool to output a structured response.
Do NOT output any text in addition to the tool call.\
"""
                        )
                    ),
                    UserMessage(
                        content=[Text(text="Recommend a single fantasy book.")]
                    ),
                    AssistantMessage(
                        content=[
                            Text(
                                text='{"title": "The Name of the Wind", "author": "Patrick Rothfuss", "vibe": "mysterious!"}'
                            )
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 16,
            },
            "structured_output_should_call_tool_scenario": {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "finish_reason": FinishReason.TOOL_USE,
                "messages": [
                    SystemMessage(
                        content=Text(
                            text="""\
When you are ready to respond to the user, call the __mirascope_formatted_output_tool__ tool to output a structured response.
Do NOT output any text in addition to the tool call.\
"""
                        )
                    ),
                    UserMessage(
                        content=[
                            Text(text="Recommend a single fantasy book in the library.")
                        ]
                    ),
                    AssistantMessage(
                        content=[
                            ToolCall(
                                id="toolu_01ARhf6AHvqvkPYAkZbPNmi3",
                                name="available_books",
                                args="{}",
                            )
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 3,
            },
            "structured_output_uses_tool_output_scenario": {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    SystemMessage(
                        content=Text(
                            text="""\
When you are ready to respond to the user, call the __mirascope_formatted_output_tool__ tool to output a structured response.
Do NOT output any text in addition to the tool call.\
"""
                        )
                    ),
                    UserMessage(
                        content=[
                            Text(text="Recommend a single fantasy book in the library.")
                        ]
                    ),
                    AssistantMessage(
                        content=[
                            ToolCall(id="call_123", name="available_books", args="{}")
                        ]
                    ),
                    UserMessage(
                        content=[
                            ToolOutput(
                                id="call_123",
                                name="available_books",
                                value=[
                                    "Wild Seed by Octavia Butler",
                                    "The Long Way to a Small Angry Planet by Becky Chambers",
                                    "Emergent Strategy by adrianne maree brown",
                                ],
                            )
                        ]
                    ),
                    AssistantMessage(
                        content=[
                            Text(
                                text='{"title": "Wild Seed", "author": "Octavia Butler", "vibe": "mysterious!"}'
                            )
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 14,
            },
            "structured_output_with_formatting_instructions_scenario": {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    SystemMessage(
                        content=Text(
                            text="""\
Pretty please output a book recommendation in JSON form.
It should have the format {title: str, author: str, vibe: str}.
Be super vibe-y with the vibe and make sure EVERYTHING IS CAPS to convey
the STRENGTH OF YOUR RECOMMENDATION!\
"""
                        )
                    ),
                    UserMessage(
                        content=[Text(text="Recommend a single fantasy book.")]
                    ),
                    AssistantMessage(
                        content=[
                            Text(
                                text='{"title": "THE NAME OF THE WIND", "author": "PATRICK ROTHFUSS", "vibe": "MYSTERIOUS"}'
                            )
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 17,
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario": {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    SystemMessage(
                        content=Text(
                            text="""\
You are a depressive LLM that only recommends sad books.
Pretty please output a book recommendation in JSON form.
It should have the format {title: str, author: str, vibe: str}.
Be super vibe-y with the vibe and make sure EVERYTHING IS CAPS to convey
the STRENGTH OF YOUR RECOMMENDATION!\
"""
                        )
                    ),
                    UserMessage(
                        content=[Text(text="Recommend a single fantasy book.")]
                    ),
                    AssistantMessage(
                        content=[
                            Text(
                                text='{"title": "THE BOOK OF LOST THINGS", "author": "JOHN CONNOLLY", "vibe": "soul_searching"}'
                            )
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 15,
            },
            "structured_output_with_nested_models_scenario": {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    SystemMessage(
                        content=Text(
                            text="""\
When you are ready to respond to the user, call the __mirascope_formatted_output_tool__ tool to output a structured response.
Do NOT output any text in addition to the tool call.\
"""
                        )
                    ),
                    UserMessage(content=[Text(text="Tell me about a book series.")]),
                    AssistantMessage(
                        content=[
                            Text(
                                text='{"series_name": "The Lord of the Rings", "author": "J.R.R. Tolkien", "book_count": 3, "books": [{"title":"The Fellowship of the Ring","author":"J.R.R. Tolkien","vibe":"mysterious!"},{"title":"The Two Towers","author":"J.R.R. Tolkien","vibe":"intriguing!"},{"title":"The Return of the King","author":"J.R.R. Tolkien","vibe":"euphoric!"}]}'
                            )
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 56,
            },
        }
    )

    assert utils.stream_response_snapshot_dict(stream_response) == expected[scenario_id]


@pytest.mark.parametrize("format_mode", FORMATTING_MODES)
@pytest.mark.parametrize("scenario_id", STRUCTURED_SCENARIO_IDS)
@pytest.mark.vcr()
def test_structured_output_all_scenarios(
    anthropic_client: llm.AnthropicClient,
    format_mode: llm.formatting.FormattingMode,
    scenario_id: str,
    request: pytest.FixtureRequest,
) -> None:
    """Test all structured output scenarios across all formatting modes."""
    scenario_data = request.getfixturevalue(scenario_id)
    llm.format(scenario_data["format"], mode=format_mode)

    try:
        response = anthropic_client.call(model_id=TEST_MODEL_ID, **scenario_data)

        try:
            output = response.format()
            if output is not None:
                actual = {
                    "type": "formatted_output",
                    "model_dump": output.model_dump(),
                }
            else:
                actual = {"type": "raw_content", "content": response.content}
        except Exception:
            actual = {"type": "raw_content", "content": response.content}

    except Exception as e:
        actual = {
            "type": "exception",
            "exception_type": type(e).__name__,
            "exception_message": str(e),
            "status_code": getattr(e, "status_code", None),
        }

    expected = snapshot(
        {
            "structured_output_basic_scenario:strict-or-tool:claude-sonnet-4-0": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "The Name of the Wind",
                    "author": "Patrick Rothfuss",
                    "vibe": "intriguing!",
                },
            },
            "structured_output_basic_scenario:strict-or-json:claude-sonnet-4-0": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "The Name of the Wind",
                    "author": "Patrick Rothfuss",
                    "vibe": "mysterious!",
                },
            },
            "structured_output_basic_scenario:strict:claude-sonnet-4-0": {
                "type": "raw_content",
                "content": [
                    Text(
                        text="""\
I'd recommend **The Name of the Wind** by Patrick Rothfuss.

It's a beautifully written story about Kvothe, a legendary figure telling his own tale at an inn. The prose is lyrical and engaging, blending magic, music, and mystery in a richly detailed world. Rothfuss has a gift for storytelling that makes even mundane moments feel magical, and the magic system based on sympathy and naming is both logical and wondrous.

Fair warning: it's the first book in an unfinished trilogy, but it works well as a standalone story and is absolutely worth reading for the journey itself.\
"""
                    )
                ],
            },
            "structured_output_basic_scenario:tool:claude-sonnet-4-0": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "The Name of the Wind",
                    "author": "Patrick Rothfuss",
                    "vibe": "intriguing!",
                },
            },
            "structured_output_basic_scenario:json:claude-sonnet-4-0": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "The Name of the Wind",
                    "author": "Patrick Rothfuss",
                    "vibe": "mysterious!",
                },
            },
            "structured_output_should_call_tool_scenario:strict-or-tool:claude-sonnet-4-0": {
                "type": "raw_content",
                "content": [
                    ToolCall(
                        id="toolu_013H65CyUX4yKL3ZmXLpwnNe",
                        name="available_books",
                        args="{}",
                    )
                ],
            },
            "structured_output_should_call_tool_scenario:strict-or-json:claude-sonnet-4-0": {
                "type": "raw_content",
                "content": [
                    ToolCall(
                        id="toolu_014LudfEVa1EJJhaRvDfuc5P",
                        name="available_books",
                        args="{}",
                    )
                ],
            },
            "structured_output_should_call_tool_scenario:strict:claude-sonnet-4-0": {
                "type": "raw_content",
                "content": [
                    Text(
                        text="I'll check what fantasy books are available in the library and recommend one for you."
                    ),
                    ToolCall(
                        id="toolu_01QyT4R5y2kQoU9YyjfDNan9",
                        name="available_books",
                        args="{}",
                    ),
                ],
            },
            "structured_output_should_call_tool_scenario:tool:claude-sonnet-4-0": {
                "type": "raw_content",
                "content": [
                    ToolCall(
                        id="toolu_01UKiwF93p7Lp9EPpJqfAJtv",
                        name="available_books",
                        args="{}",
                    )
                ],
            },
            "structured_output_should_call_tool_scenario:json:claude-sonnet-4-0": {
                "type": "raw_content",
                "content": [
                    ToolCall(
                        id="toolu_01XYTYorBzciXcpfw5asP4Wz",
                        name="available_books",
                        args="{}",
                    )
                ],
            },
            "structured_output_uses_tool_output_scenario:strict-or-tool:claude-sonnet-4-0": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "Wild Seed",
                    "author": "Octavia Butler",
                    "vibe": "mysterious!",
                },
            },
            "structured_output_uses_tool_output_scenario:strict-or-json:claude-sonnet-4-0": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "Wild Seed",
                    "author": "Octavia Butler",
                    "vibe": "mysterious!",
                },
            },
            "structured_output_uses_tool_output_scenario:strict:claude-sonnet-4-0": {
                "type": "raw_content",
                "content": [
                    Text(
                        text="""\
Based on the available books in the library, I'd recommend **"Wild Seed" by Octavia Butler**. This is a compelling fantasy/science fiction novel that follows the story of Doro, an immortal being who has lived for thousands of years by taking over other people's bodies, and Anyanwu, a shape-shifting healer with extraordinary powers. \n\

Butler masterfully weaves themes of power, identity, and survival into a narrative that spans centuries and continents. The book explores complex relationships and moral questions while delivering fantastic world-building and character development. It's considered one of Butler's finest works and a classic in speculative fiction that blends fantasy elements with profound social commentary.\
"""
                    )
                ],
            },
            "structured_output_uses_tool_output_scenario:tool:claude-sonnet-4-0": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "Wild Seed",
                    "author": "Octavia Butler",
                    "vibe": "mysterious!",
                },
            },
            "structured_output_uses_tool_output_scenario:json:claude-sonnet-4-0": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "Wild Seed",
                    "author": "Octavia Butler",
                    "vibe": "mysterious!",
                },
            },
            "structured_output_with_formatting_instructions_scenario:strict-or-tool:claude-sonnet-4-0": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "THE NAME OF THE WIND",
                    "author": "PATRICK ROTHFUSS",
                    "vibe": "INTRIGUING",
                },
            },
            "structured_output_with_formatting_instructions_scenario:strict-or-json:claude-sonnet-4-0": {
                "type": "raw_content",
                "content": [
                    Text(
                        text="""\
```json
{
  "title": "THE NAME OF THE WIND",
  "author": "PATRICK ROTHFUSS", \n\
  "vibe": "ABSOLUTELY LEGENDARY STORYTELLING WITH A BARD WHO COULD CHARM THE STARS FROM THE SKY AND MAGIC THAT FEELS LIKE PURE WONDER COURSING THROUGH YOUR VEINS!"
}
```\
"""
                    )
                ],
            },
            "structured_output_with_formatting_instructions_scenario:strict:claude-sonnet-4-0": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "THE NAME OF THE WIND",
                    "author": "PATRICK ROTHFUSS",
                    "vibe": "ABSOLUTELY LEGENDARY STORYTELLING MAGIC WITH A BARD WHO'S BASICALLY THE FANTASY EQUIVALENT OF A ROCK STAR WIZARD AND THE PROSE WILL MAKE YOU WEEP ACTUAL TEARS OF BEAUTY!",
                },
            },
            "structured_output_with_formatting_instructions_scenario:tool:claude-sonnet-4-0": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "THE NAME OF THE WIND",
                    "author": "PATRICK ROTHFUSS",
                    "vibe": "MYSTERIOUS",
                },
            },
            "structured_output_with_formatting_instructions_scenario:json:claude-sonnet-4-0": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "THE NAME OF THE WIND",
                    "author": "PATRICK ROTHFUSS",
                    "vibe": "ABSOLUTELY MESMERIZING STORYTELLING MAGIC THAT WILL CONSUME YOUR SOUL WITH BEAUTIFUL PROSE AND A LEGENDARY HERO'S ORIGIN STORY TOLD WITH BARDIC PERFECTION!",
                },
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario:strict-or-tool:claude-sonnet-4-0": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "THE ROAD",
                    "author": "CORMAC MCCARTHY",
                    "vibe": "soul_searching",
                },
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario:strict-or-json:claude-sonnet-4-0": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "THE ROAD",
                    "author": "CORMAC MCCARTHY",
                    "vibe": "ABSOLUTELY SOUL-CRUSHING POST-APOCALYPTIC BLEAKNESS WHERE A FATHER AND SON TRUDGE THROUGH AN ASH-COVERED WASTELAND OF HUMAN DESPAIR AND HOPELESSNESS - THE PERFECT BOOK TO MAKE YOU QUESTION THE VERY MEANING OF EXISTENCE AND FEEL THE WEIGHT OF INEVITABLE DOOM PRESSING DOWN ON YOUR SPIRIT!",
                },
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario:strict:claude-sonnet-4-0": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "THE BOOK OF LOST THINGS",
                    "author": "JOHN CONNOLLY",
                    "vibe": "A DEVASTATINGLY BEAUTIFUL TALE OF A BOY WHO ESCAPES INTO A DARK FAIRY TALE WORLD TO COPE WITH HIS MOTHER'S DEATH, ONLY TO FIND THAT EVEN FANTASY REALMS ARE FILLED WITH LOSS, BETRAYAL, AND THE CRUSHING WEIGHT OF GROWING UP TOO SOON. PREPARE TO HAVE YOUR HEART ABSOLUTELY SHATTERED BY THE MELANCHOLY MAGIC!",
                },
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario:tool:claude-sonnet-4-0": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "THE BOOK OF LOST THINGS",
                    "author": "JOHN CONNOLLY",
                    "vibe": "soul_searching",
                },
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario:json:claude-sonnet-4-0": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "THE ROAD",
                    "author": "CORMAC MCCARTHY",
                    "vibe": "A SOUL-CRUSHING POST-APOCALYPTIC JOURNEY THROUGH A DEAD WORLD WHERE A FATHER AND SON TRUDGE THROUGH ASH AND DESPAIR, CLINGING TO EACH OTHER AS THE LAST EMBER OF HUMANITY FLICKERS OUT IN AN ENDLESS GRAY WASTELAND OF HOPELESSNESS!",
                },
            },
            "structured_output_with_nested_models_scenario:strict-or-tool:claude-sonnet-4-0": {
                "type": "formatted_output",
                "model_dump": {
                    "series_name": "The Expanse",
                    "author": "James S.A. Corey",
                    "books": [
                        {
                            "title": "Leviathan Wakes",
                            "author": "James S.A. Corey",
                            "vibe": "mysterious!",
                        },
                        {
                            "title": "Caliban's War",
                            "author": "James S.A. Corey",
                            "vibe": "intriguing!",
                        },
                        {
                            "title": "Abaddon's Gate",
                            "author": "James S.A. Corey",
                            "vibe": "soul_searching!",
                        },
                        {
                            "title": "Cibola Burn",
                            "author": "James S.A. Corey",
                            "vibe": "mysterious!",
                        },
                        {
                            "title": "Nemesis Games",
                            "author": "James S.A. Corey",
                            "vibe": "euphoric!",
                        },
                        {
                            "title": "Babylon's Ashes",
                            "author": "James S.A. Corey",
                            "vibe": "intriguing!",
                        },
                        {
                            "title": "Persepolis Rising",
                            "author": "James S.A. Corey",
                            "vibe": "soul_searching!",
                        },
                        {
                            "title": "Tiamat's Wrath",
                            "author": "James S.A. Corey",
                            "vibe": "mysterious!",
                        },
                        {
                            "title": "Leviathan Falls",
                            "author": "James S.A. Corey",
                            "vibe": "euphoric!",
                        },
                    ],
                    "book_count": 9,
                },
            },
            "structured_output_with_nested_models_scenario:strict-or-json:claude-sonnet-4-0": {
                "type": "formatted_output",
                "model_dump": {
                    "series_name": "The Expanse",
                    "author": "James S.A. Corey",
                    "books": [
                        {
                            "title": "Leviathan Wakes",
                            "author": "James S.A. Corey",
                            "vibe": "mysterious!",
                        },
                        {
                            "title": "Caliban's War",
                            "author": "James S.A. Corey",
                            "vibe": "intruiging!",
                        },
                        {
                            "title": "Abaddon's Gate",
                            "author": "James S.A. Corey",
                            "vibe": "euphoric!",
                        },
                        {
                            "title": "Cibola Burn",
                            "author": "James S.A. Corey",
                            "vibe": "soul_searching!",
                        },
                        {
                            "title": "Nemesis Games",
                            "author": "James S.A. Corey",
                            "vibe": "mysterious!",
                        },
                    ],
                    "book_count": 5,
                },
            },
            "structured_output_with_nested_models_scenario:strict:claude-sonnet-4-0": {
                "type": "raw_content",
                "content": [
                    Text(
                        text="""\
I'd be happy to tell you about a book series! Let me share one of my favorites:

**The Expanse** by James S.A. Corey (pen name for Daniel Abraham and Ty Franck)

This is a nine-book science fiction series that takes place a few hundred years in the future when humanity has colonized the solar system. The series follows:

**Setting**: A politically complex world where Earth, Mars, and the Belt (asteroid miners) are in constant tension. Space travel is realistic - no faster-than-light travel, and the physics of acceleration/deceleration matter.

**Main Characters**: \n\
- James Holden and his crew aboard the ship *Rocinante*
- Detective Josephus Miller \n\
- Politician Chrisjen Avasarala
- Martian Marine Bobbie Draper

**What makes it great**:
- Realistic space politics and physics
- Complex moral dilemmas
- Excellent character development across multiple perspectives
- Blends mystery, politics, and hard sci-fi
- Was adapted into a acclaimed TV series

The first book is *Leviathan Wakes* (2011), and it works well as both a standalone and series starter.

Would you like me to tell you about a different genre or series? Or would you prefer recommendations based on your specific interests?\
"""
                    )
                ],
            },
            "structured_output_with_nested_models_scenario:tool:claude-sonnet-4-0": {
                "type": "formatted_output",
                "model_dump": {
                    "series_name": "The Expanse",
                    "author": "James S.A. Corey",
                    "books": [
                        {
                            "title": "Leviathan Wakes",
                            "author": "James S.A. Corey",
                            "vibe": "mysterious!",
                        },
                        {
                            "title": "Caliban's War",
                            "author": "James S.A. Corey",
                            "vibe": "intruiging!",
                        },
                        {
                            "title": "Abaddon's Gate",
                            "author": "James S.A. Corey",
                            "vibe": "mysterious!",
                        },
                        {
                            "title": "Cibola Burn",
                            "author": "James S.A. Corey",
                            "vibe": "soul_searching!",
                        },
                        {
                            "title": "Nemesis Games",
                            "author": "James S.A. Corey",
                            "vibe": "intruiging!",
                        },
                        {
                            "title": "Babylon's Ashes",
                            "author": "James S.A. Corey",
                            "vibe": "euphoric!",
                        },
                        {
                            "title": "Persepolis Rising",
                            "author": "James S.A. Corey",
                            "vibe": "mysterious!",
                        },
                        {
                            "title": "Tiamat's Wrath",
                            "author": "James S.A. Corey",
                            "vibe": "soul_searching!",
                        },
                        {
                            "title": "Leviathan Falls",
                            "author": "James S.A. Corey",
                            "vibe": "euphoric!",
                        },
                    ],
                    "book_count": 9,
                },
            },
            "structured_output_with_nested_models_scenario:json:claude-sonnet-4-0": {
                "type": "formatted_output",
                "model_dump": {
                    "series_name": "The Expanse",
                    "author": "James S.A. Corey",
                    "books": [
                        {
                            "title": "Leviathan Wakes",
                            "author": "James S.A. Corey",
                            "vibe": "mysterious!",
                        },
                        {
                            "title": "Caliban's War",
                            "author": "James S.A. Corey",
                            "vibe": "intruiging!",
                        },
                        {
                            "title": "Abaddon's Gate",
                            "author": "James S.A. Corey",
                            "vibe": "euphoric!",
                        },
                        {
                            "title": "Cibola Burn",
                            "author": "James S.A. Corey",
                            "vibe": "soul_searching!",
                        },
                        {
                            "title": "Nemesis Games",
                            "author": "James S.A. Corey",
                            "vibe": "mysterious!",
                        },
                    ],
                    "book_count": 5,
                },
            },
        }
    )

    assert actual == expected[f"{scenario_id}:{format_mode}:{TEST_MODEL_ID}"]
