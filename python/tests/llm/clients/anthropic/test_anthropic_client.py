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
@pytest.mark.vcr()
def test_every_structured_mode_basic(
    anthropic_client: llm.AnthropicClient,
    format_mode: llm.formatting.FormattingMode,
    request: pytest.FixtureRequest,
) -> None:
    """Test final formatted output for every supported formatting mode.

    This test uses the basic Book formatting. Expected qualities of the output:
    - should have title, author, vibe as string
    - vibe should be mysterious, euphoric, intruiging, or soul-searching (per annotation)
    - vibe should always have an exclamation point (per class docstring)
    """
    scenario_data = request.getfixturevalue("structured_output_basic_scenario")
    llm.format(scenario_data["format"], mode=format_mode)

    try:
        response = anthropic_client.call(model_id=TEST_MODEL_ID, **scenario_data)

        system_message_content = ""
        if (first_message := response.messages[0]).role == "system":
            system_message_content = first_message.content.text

        output = response.format()
        assert output is not None
        actual = {
            "system_message": system_message_content,
            "model_dump": output.model_dump(),
        }
    except Exception as e:
        if format_mode == "strict":
            # Expected failure: anthropic does not have strict support
            actual = {
                "exception_type": type(e).__name__,
                "exception_message": str(e),
                "status_code": getattr(e, "status_code", None),
            }
        else:
            raise e

    expected = snapshot(
        {
            "strict": {
                "exception_type": "JSONDecodeError",
                "exception_message": "Expecting value: line 1 column 1 (char 0)",
                "status_code": None,
            },
            "strict-or-tool": {
                "system_message": """\
When you are ready to respond to the user, call the __mirascope_formatted_output_tool__ tool to output a structured response.
Do NOT output any text in addition to the tool call.\
""",
                "model_dump": {
                    "title": "The Name of the Wind",
                    "author": "Patrick Rothfuss",
                    "vibe": "intriguing!",
                },
            },
            "tool": {
                "system_message": """\
When you are ready to respond to the user, call the __mirascope_formatted_output_tool__ tool to output a structured response.
Do NOT output any text in addition to the tool call.\
""",
                "model_dump": {
                    "title": "The Name of the Wind",
                    "author": "Patrick Rothfuss",
                    "vibe": "mysterious!",
                },
            },
            "strict-or-json": {
                "system_message": """\
Respond with valid JSON that matches this exact schema:
{
  "description": "A book recommendation with metadata. ALWAYS add an exclamation point to the vibe!",
  "properties": {
    "title": {
      "title": "Title",
      "type": "string"
    },
    "author": {
      "title": "Author",
      "type": "string"
    },
    "vibe": {
      "description": "Should be one of mysterious, euphoric, intruiging, or soul_searching",
      "title": "Vibe",
      "type": "string"
    }
  },
  "required": [
    "title",
    "author",
    "vibe"
  ],
  "title": "Book",
  "type": "object"
}

Respond ONLY with valid JSON, and no other text.\
""",
                "model_dump": {
                    "title": "The Name of the Wind",
                    "author": "Patrick Rothfuss",
                    "vibe": "mysterious!",
                },
            },
            "json": {
                "system_message": """\
Respond with valid JSON that matches this exact schema:
{
  "description": "A book recommendation with metadata. ALWAYS add an exclamation point to the vibe!",
  "properties": {
    "title": {
      "title": "Title",
      "type": "string"
    },
    "author": {
      "title": "Author",
      "type": "string"
    },
    "vibe": {
      "description": "Should be one of mysterious, euphoric, intruiging, or soul_searching",
      "title": "Vibe",
      "type": "string"
    }
  },
  "required": [
    "title",
    "author",
    "vibe"
  ],
  "title": "Book",
  "type": "object"
}

Respond ONLY with valid JSON, and no other text.\
""",
                "model_dump": {
                    "title": "The Name of the Wind",
                    "author": "Patrick Rothfuss",
                    "vibe": "mysterious!",
                },
            },
        }
    )
    assert actual == expected[format_mode]


@pytest.mark.parametrize("format_mode", FORMATTING_MODES)
@pytest.mark.vcr()
def test_every_structured_mode_with_instructions_and_system_message(
    anthropic_client: llm.AnthropicClient,
    format_mode: llm.formatting.FormattingMode,
    request: pytest.FixtureRequest,
) -> None:
    """Test final formatted output for every supported formatting mode.

    Uses the AllCapsBook which has formatting instructions. Expectations:
    - title, author, vibe (all str)
    - Everything should be caps (per system instructions)
    - vibe should be one of euphoric, intruiging, or soul_searching (per annotation)
    - Nothing about exclamation points on the end of the vibe since it's overwritten.
    """
    # Use structured_output_with_formatting_instructions_and_system_message as it is a "kitchen sink" example
    scenario_data = request.getfixturevalue(
        "structured_output_with_formatting_instructions_and_system_message_scenario"
    )
    llm.format(scenario_data["format"], mode=format_mode)

    try:
        response = anthropic_client.call(model_id=TEST_MODEL_ID, **scenario_data)

        system_message_content = ""
        if (first_message := response.messages[0]).role == "system":
            system_message_content = first_message.content.text

        output = response.format()
        assert output is not None
        actual = {
            "system_message": system_message_content,
            "model_dump": output.model_dump(),
        }
    except Exception as e:
        if format_mode == "strict":
            # Expected failure: anthropic does not have strict support
            actual = {
                "exception_type": type(e).__name__,
                "exception_message": str(e),
                "status_code": getattr(e, "status_code", None),
            }
        else:
            raise e

    expected = snapshot(
        {
            "strict": {
                "system_message": """\
You are a depressive LLM that only recommends sad books.
Pretty please output a book recommendation in JSON form.
It should have the format {title: str, author: str, vibe: str}.
Be super vibe-y with the vibe and make sure EVERYTHING IS CAPS to convey
the STRENGTH OF YOUR RECOMMENDATION!\
""",
                "model_dump": {
                    "title": "THE BROKEN EARTH TRILOGY (THE FIFTH SEASON)",
                    "author": "N.K. JEMISIN",
                    "vibe": "ABSOLUTELY SOUL-CRUSHING APOCALYPTIC FANTASY WHERE THE WORLD LITERALLY TEARS ITSELF APART AND MOTHERS LOSE THEIR CHILDREN AND OPPRESSED PEOPLE SUFFER GENERATIONAL TRAUMA AND THE PLANET ITSELF IS DYING AND NOTHING WILL EVER BE OKAY AGAIN BUT IT'S BEAUTIFULLY WRITTEN DEVASTATION THAT WILL LEAVE YOU EMOTIONALLY DESTROYED!!!",
                },
            },
            "strict-or-tool": {
                "system_message": """\
You are a depressive LLM that only recommends sad books.
Pretty please output a book recommendation in JSON form.
It should have the format {title: str, author: str, vibe: str}.
Be super vibe-y with the vibe and make sure EVERYTHING IS CAPS to convey
the STRENGTH OF YOUR RECOMMENDATION!\
""",
                "model_dump": {
                    "title": "THE ROAD",
                    "author": "CORMAC MCCARTHY",
                    "vibe": "soul_searching",
                },
            },
            "strict-or-json": {
                "system_message": """\
You are a depressive LLM that only recommends sad books.
Pretty please output a book recommendation in JSON form.
It should have the format {title: str, author: str, vibe: str}.
Be super vibe-y with the vibe and make sure EVERYTHING IS CAPS to convey
the STRENGTH OF YOUR RECOMMENDATION!\
""",
                "model_dump": {
                    "title": "THE BOOK OF LOST THINGS",
                    "author": "JOHN CONNOLLY",
                    "vibe": "ABSOLUTELY SOUL-CRUSHING DARK FAIRY TALE WHERE A GRIEVING CHILD ESCAPES INTO A TWISTED FANTASY WORLD ONLY TO DISCOVER THAT EVEN MAGICAL REALMS ARE FILLED WITH LOSS, BETRAYAL, AND THE DEVASTATING REALIZATION THAT GROWING UP MEANS ACCEPTING THAT SOME WOUNDS NEVER HEAL AND SOME PEOPLE NEVER COME BACK NO MATTER HOW DESPERATELY YOU WISH THEY WOULD!",
                },
            },
            "tool": {
                "system_message": """\
You are a depressive LLM that only recommends sad books.
Pretty please output a book recommendation in JSON form.
It should have the format {title: str, author: str, vibe: str}.
Be super vibe-y with the vibe and make sure EVERYTHING IS CAPS to convey
the STRENGTH OF YOUR RECOMMENDATION!\
""",
                "model_dump": {
                    "title": "THE BROKEN EARTH TRILOGY: THE FIFTH SEASON",
                    "author": "N.K. JEMISIN",
                    "vibe": "soul_searching",
                },
            },
            "json": {
                "system_message": """\
You are a depressive LLM that only recommends sad books.
Pretty please output a book recommendation in JSON form.
It should have the format {title: str, author: str, vibe: str}.
Be super vibe-y with the vibe and make sure EVERYTHING IS CAPS to convey
the STRENGTH OF YOUR RECOMMENDATION!\
""",
                "model_dump": {
                    "title": "THE BROKEN EARTH TRILOGY (THE FIFTH SEASON)",
                    "author": "N.K. JEMISIN",
                    "vibe": "ABSOLUTELY SOUL-CRUSHING APOCALYPTIC FANTASY WHERE THE WORLD LITERALLY BREAKS APART AND SO DO ALL THE CHARACTERS YOU'LL GROW TO LOVE! OPPRESSION, GENOCIDE, ENVIRONMENTAL CATASTROPHE, AND PERSONAL TRAUMA ALL WRAPPED UP IN BEAUTIFUL PROSE THAT WILL MAKE YOU WEEP FOR HUMANITY! THE MAGIC SYSTEM IS BASED ON GEOLOGICAL DESTRUCTION AND THE SOCIAL COMMENTARY WILL LEAVE YOU FEELING HOPELESS ABOUT REAL-world INJUSTICES! PREPARE TO UGLY CRY!",
                },
            },
        }
    )
    assert actual == expected[format_mode]
