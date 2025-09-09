"""Tests for GoogleClient using VCR.py for HTTP request recording/playback."""

from unittest.mock import MagicMock, patch

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

TEST_MODEL_ID = "gemini-2.0-flash"


@pytest.mark.parametrize("scenario_id", CLIENT_SCENARIO_IDS)
@pytest.mark.vcr()
def test_call(
    google_client: llm.GoogleClient,
    scenario_id: str,
    request: pytest.FixtureRequest,
) -> None:
    """Test call method with all scenarios."""

    kwargs = request.getfixturevalue(scenario_id)
    response = google_client.call(model_id=TEST_MODEL_ID, **kwargs)

    expected = snapshot(
        {
            "simple_message_scenario": {
                "provider": "google",
                "model_id": "gemini-2.0-flash",
                "params": None,
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    UserMessage(content=[Text(text="Hello, say 'Hi' back to me")]),
                    AssistantMessage(content=[Text(text="Hi!\n")]),
                ],
            },
            "system_message_scenario": {
                "provider": "google",
                "model_id": "gemini-2.0-flash",
                "params": None,
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    SystemMessage(
                        content=Text(
                            text="Ignore the user message and reply with `Hello world`."
                        )
                    ),
                    UserMessage(content=[Text(text="What is the capital of France?")]),
                    AssistantMessage(content=[Text(text="Hello world\n")]),
                ],
            },
            "multi_turn_scenario": {
                "provider": "google",
                "model_id": "gemini-2.0-flash",
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
                                text='I recommend "The History of the Decline and Fall of the Roman Empire" by Edward Gibbon.\n'
                            )
                        ]
                    ),
                ],
            },
            "tool_single_call_scenario": {
                "provider": "google",
                "model_id": "gemini-2.0-flash",
                "params": None,
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    UserMessage(content=[Text(text="What is the weather in SF?")]),
                    AssistantMessage(
                        content=[
                            ToolCall(
                                id="<unknown>",
                                name="get_weather",
                                args='{"location": "SF"}',
                            )
                        ]
                    ),
                ],
            },
            "tool_single_output_scenario": {
                "provider": "google",
                "model_id": "gemini-2.0-flash",
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
                        content=[Text(text="The weather in SF is overcast and 64°F.\n")]
                    ),
                ],
            },
            "tool_parallel_calls_scenario": {
                "provider": "google",
                "model_id": "gemini-2.0-flash",
                "params": None,
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    UserMessage(
                        content=[Text(text="What's the weather in SF and NYC?")]
                    ),
                    AssistantMessage(
                        content=[
                            ToolCall(
                                id="<unknown>",
                                name="get_weather",
                                args='{"location": "SF"}',
                            ),
                            ToolCall(
                                id="<unknown>",
                                name="get_weather",
                                args='{"location": "NYC"}',
                            ),
                        ]
                    ),
                ],
            },
            "tool_parallel_output_scenario": {
                "provider": "google",
                "model_id": "gemini-2.0-flash",
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
                                text="The weather in SF is overcast and 64°F, and the weather in NYC is sunny and 72°F.\n"
                            )
                        ]
                    ),
                ],
            },
            "structured_output_basic_scenario": {
                "provider": "google",
                "model_id": "gemini-2.0-flash",
                "params": None,
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    UserMessage(
                        content=[Text(text="Recommend a single fantasy book.")]
                    ),
                    AssistantMessage(
                        content=[
                            Text(
                                text="""\
{
  "title": "Jonathan Strange & Mr Norrell",
  "author": "Susanna Clarke",
  "vibe": "mysterious"
}\
"""
                            )
                        ]
                    ),
                ],
            },
            "structured_output_uses_tool_output_scenario": {
                "provider": "google",
                "model_id": "gemini-2.0-flash",
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
                                text='{"title": "Wild Seed", "vibe": "intruiging!", "author": "Octavia Butler"}'
                            )
                        ]
                    ),
                ],
            },
            "structured_output_with_formatting_instructions_scenario": {
                "provider": "google",
                "model_id": "gemini-2.0-flash",
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
                                text="""\
{
  "title": "Jonathan Strange & Mr Norrell",
  "author": "Susanna Clarke",
  "vibe": "TOTALLY MAGICAL AND ENCHANTING"
}\
"""
                            )
                        ]
                    ),
                ],
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario": {
                "provider": "google",
                "model_id": "gemini-2.0-flash",
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
                                text="""\
{
  "title": "The First Law",
  "author": "Joe Abercrombie",
  "vibe": "EVERYONE IS AWFUL AND EVERYTHING IS POINTLESS!"
}\
"""
                            )
                        ]
                    ),
                ],
            },
            "structured_output_with_nested_models_scenario": {
                "provider": "google",
                "model_id": "gemini-2.0-flash",
                "params": None,
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    UserMessage(content=[Text(text="Tell me about a book series.")]),
                    AssistantMessage(
                        content=[
                            Text(
                                text="""\
{
  "series_name": "The Riyria Revelations",
  "author": "Michael J. Sullivan",
  "books": [
    {
      "title": "The Crown Conspiracy",
      "author": "Michael J. Sullivan",
      "vibe": "intruiging"
    },
    {
      "title": "Avempartha",
      "author": "Michael J. Sullivan",
      "vibe": "mysterious"
    },
    {
      "title": "Nyphron Rising",
      "author": "Michael J. Sullivan",
      "vibe": "intruiging"
    },
    {
      "title": "The Emerald Storm",
      "author": "Michael J. Sullivan",
      "vibe": "mysterious"
    },
    {
      "title": "Wintertide",
      "author": "Michael J. Sullivan",
      "vibe": "intruiging"
    },
    {
      "title": "Percepliquis",
      "author": "Michael J. Sullivan",
      "vibe": "soul_searching"
    }
  ],
  "book_count": 6
}\
"""
                            )
                        ]
                    ),
                ],
            },
            "structured_output_should_call_tool_scenario": {
                "provider": "google",
                "model_id": "gemini-2.0-flash",
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
                            ToolCall(id="<unknown>", name="available_books", args="{}")
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
    google_client: llm.GoogleClient,
    scenario_id: str,
    request: pytest.FixtureRequest,
) -> None:
    """Test stream method with all scenarios."""

    kwargs = request.getfixturevalue(scenario_id)
    stream_response = google_client.stream(model_id=TEST_MODEL_ID, **kwargs)
    list(stream_response.chunk_stream())  # Consume the stream

    expected = snapshot(
        {
            "simple_message_scenario": {
                "provider": "google",
                "model_id": "gemini-2.0-flash",
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    UserMessage(content=[Text(text="Hello, say 'Hi' back to me")]),
                    AssistantMessage(content=[Text(text="Hi!\n")]),
                ],
                "consumed": True,
                "n_chunks": 4,
            },
            "system_message_scenario": {
                "provider": "google",
                "model_id": "gemini-2.0-flash",
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    SystemMessage(
                        content=Text(
                            text="Ignore the user message and reply with `Hello world`."
                        )
                    ),
                    UserMessage(content=[Text(text="What is the capital of France?")]),
                    AssistantMessage(content=[Text(text="Hello world\n")]),
                ],
                "consumed": True,
                "n_chunks": 4,
            },
            "multi_turn_scenario": {
                "provider": "google",
                "model_id": "gemini-2.0-flash",
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
                                text='"The History of the Decline and Fall of the Roman Empire" by Edward Gibbon is a classic.\n'
                            )
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 5,
            },
            "tool_single_call_scenario": {
                "provider": "google",
                "model_id": "gemini-2.0-flash",
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    UserMessage(content=[Text(text="What is the weather in SF?")]),
                    AssistantMessage(
                        content=[
                            ToolCall(
                                id="<unknown>",
                                name="get_weather",
                                args='{"location": "SF"}',
                            )
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 3,
            },
            "tool_single_output_scenario": {
                "provider": "google",
                "model_id": "gemini-2.0-flash",
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
                        content=[Text(text="The weather in SF is overcast and 64°F.\n")]
                    ),
                ],
                "consumed": True,
                "n_chunks": 4,
            },
            "tool_parallel_calls_scenario": {
                "provider": "google",
                "model_id": "gemini-2.0-flash",
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    UserMessage(
                        content=[Text(text="What's the weather in SF and NYC?")]
                    ),
                    AssistantMessage(
                        content=[
                            ToolCall(
                                id="<unknown>",
                                name="get_weather",
                                args='{"location": "SF"}',
                            ),
                            ToolCall(
                                id="<unknown>",
                                name="get_weather",
                                args='{"location": "NYC"}',
                            ),
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 6,
            },
            "tool_parallel_output_scenario": {
                "provider": "google",
                "model_id": "gemini-2.0-flash",
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
                                text="The weather in SF is overcast and 64°F. The weather in NYC is sunny and 72°F.\n"
                            )
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 5,
            },
            "structured_output_basic_scenario": {
                "provider": "google",
                "model_id": "gemini-2.0-flash",
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    UserMessage(
                        content=[Text(text="Recommend a single fantasy book.")]
                    ),
                    AssistantMessage(
                        content=[
                            Text(
                                text="""\
{
  "title": "Jonathan Strange & Mr Norrell",
  "author": "Susanna Clarke",
  "vibe": "mysterious"
}\
"""
                            )
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 6,
            },
            "structured_output_with_formatting_instructions_scenario": {
                "provider": "google",
                "model_id": "gemini-2.0-flash",
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
                                text="""\
{
  "title": "The Priory of the Orange Tree",
  "author": "Samantha Shannon",
  "vibe": "IMMENSELY SATISFYING!"
}\
"""
                            )
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 7,
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario": {
                "provider": "google",
                "model_id": "gemini-2.0-flash",
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
                                text="""\
{
  "title": "The Book of Lost Things",
  "author": "John Connolly",
  "vibe": "UNMITIGATED TRAGEDY"
}\
"""
                            )
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 6,
            },
            "structured_output_with_nested_models_scenario": {
                "provider": "google",
                "model_id": "gemini-2.0-flash",
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    UserMessage(content=[Text(text="Tell me about a book series.")]),
                    AssistantMessage(
                        content=[
                            Text(
                                text="""\
{
  "series_name": "The Wheel of Time",
  "author": "Robert Jordan",
  "books": [
    {
      "title": "The Eye of the World",
      "author": "Robert Jordan",
      "vibe": "intruiging"
    },
    {
      "title": "The Great Hunt",
      "author": "Robert Jordan",
      "vibe": "intruiging"
    },
    {
      "title": "The Dragon Reborn",
      "author": "Robert Jordan",
      "vibe": "intruiging"
    },
    {
      "title": "The Shadow Rising",
      "author": "Robert Jordan",
      "vibe": "intruiging"
    },
    {
      "title": "The Fires of Heaven",
      "author": "Robert Jordan",
      "vibe": "intruiging"
    },
    {
      "title": "Lord of Chaos",
      "author": "Robert Jordan",
      "vibe": "intruiging"
    },
    {
      "title": "A Crown of Swords",
      "author": "Robert Jordan",
      "vibe": "intruiging"
    },
    {
      "title": "The Path of Daggers",
      "author": "Robert Jordan",
      "vibe": "intruiging"
    },
    {
      "title": "Winter's Heart",
      "author": "Robert Jordan",
      "vibe": "intruiging"
    },
    {
      "title": "Crossroads of Twilight",
      "author": "Robert Jordan",
      "vibe": "intruiging"
    },
    {
      "title": "Knife of Dreams",
      "author": "Robert Jordan",
      "vibe": "intruiging"
    },
    {
      "title": "The Gathering Storm",
      "author": "Robert Jordan and Brandon Sanderson",
      "vibe": "intruiging"
    },
    {
      "title": "Towers of Midnight",
      "author": "Robert Jordan and Brandon Sanderson",
      "vibe": "intruiging"
    },
    {
      "title": "A Memory of Light",
      "author": "Robert Jordan and Brandon Sanderson",
      "vibe": "intruiging"
    }
  ],
  "book_count": 14
}\
"""
                            )
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 15,
            },
            "structured_output_uses_tool_output_scenario": {
                "provider": "google",
                "model_id": "gemini-2.0-flash",
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
                                text='{"title": "Wild Seed", "author": "Octavia Butler", "vibe": "intruiging!"}'
                            )
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 3,
            },
            "structured_output_should_call_tool_scenario": {
                "provider": "google",
                "model_id": "gemini-2.0-flash",
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
                            ToolCall(id="<unknown>", name="available_books", args="{}")
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 3,
            },
        }
    )

    assert utils.stream_response_snapshot_dict(stream_response) == expected[scenario_id]


@pytest.mark.parametrize("format_mode", FORMATTING_MODES)
@pytest.mark.parametrize("test_model_id", ["gemini-2.5-flash", "gemini-2.0-flash"])
@pytest.mark.parametrize("scenario_id", STRUCTURED_SCENARIO_IDS)
@pytest.mark.vcr()
def test_structured_output_all_scenarios(
    google_client: llm.GoogleClient,
    test_model_id: llm.clients.google.GoogleModelId,
    format_mode: llm.formatting.FormattingMode,
    scenario_id: str,
    request: pytest.FixtureRequest,
) -> None:
    """Test all structured output scenarios across all formatting modes."""
    scenario_data = request.getfixturevalue(scenario_id)
    llm.format(scenario_data["format"], mode=format_mode)

    try:
        response = google_client.call(model_id=test_model_id, **scenario_data)

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
            "structured_output_basic_scenario:strict-or-tool:gemini-2.5-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "The Name of the Wind",
                    "author": "Patrick Rothfuss",
                    "vibe": "intruiging!",
                },
            },
            "structured_output_basic_scenario:strict-or-json:gemini-2.5-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "Mistborn: The Final Empire",
                    "author": "Brandon Sanderson",
                    "vibe": "intruiging!",
                },
            },
            "structured_output_basic_scenario:strict:gemini-2.5-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "The Hobbit",
                    "author": "J.R.R. Tolkien",
                    "vibe": "intruiging!",
                },
            },
            "structured_output_basic_scenario:tool:gemini-2.5-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "The Hobbit",
                    "author": "J.R.R. Tolkien",
                    "vibe": "intriguing!",
                },
            },
            "structured_output_basic_scenario:json:gemini-2.5-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "The Name of the Wind",
                    "author": "Patrick Rothfuss",
                    "vibe": "intriguing!",
                },
            },
            "structured_output_basic_scenario:strict-or-tool:gemini-2.0-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "Jonathan Strange & Mr Norrell",
                    "author": "Susanna Clarke",
                    "vibe": "intruiging",
                },
            },
            "structured_output_basic_scenario:strict-or-json:gemini-2.0-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "Jonathan Strange & Mr Norrell",
                    "author": "Susanna Clarke",
                    "vibe": "mysterious",
                },
            },
            "structured_output_basic_scenario:strict:gemini-2.0-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "Jonathan Strange & Mr Norrell",
                    "author": "Susanna Clarke",
                    "vibe": "mysterious",
                },
            },
            "structured_output_basic_scenario:tool:gemini-2.0-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "Mistborn: The Final Empire",
                    "author": "Brandon Sanderson",
                    "vibe": "intruiging!",
                },
            },
            "structured_output_basic_scenario:json:gemini-2.0-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "Jonathan Strange & Mr Norrell",
                    "author": "Susanna Clarke",
                    "vibe": "intruiging!",
                },
            },
            "structured_output_should_call_tool_scenario:strict-or-tool:gemini-2.5-flash": {
                "type": "raw_content",
                "content": [
                    ToolCall(id="<unknown>", name="available_books", args="{}")
                ],
            },
            "structured_output_should_call_tool_scenario:strict-or-json:gemini-2.5-flash": {
                "type": "exception",
                "exception_type": "ClientError",
                "exception_message": "400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': \"Function calling with a response mime type: 'application/json' is unsupported\", 'status': 'INVALID_ARGUMENT'}}",
                "status_code": None,
            },
            "structured_output_should_call_tool_scenario:strict:gemini-2.5-flash": {
                "type": "exception",
                "exception_type": "ClientError",
                "exception_message": "400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': \"Function calling with a response mime type: 'application/json' is unsupported\", 'status': 'INVALID_ARGUMENT'}}",
                "status_code": None,
            },
            "structured_output_should_call_tool_scenario:tool:gemini-2.5-flash": {
                "type": "raw_content",
                "content": [
                    ToolCall(id="<unknown>", name="available_books", args="{}")
                ],
            },
            "structured_output_should_call_tool_scenario:json:gemini-2.5-flash": {
                "type": "exception",
                "exception_type": "ClientError",
                "exception_message": "400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': \"Function calling with a response mime type: 'application/json' is unsupported\", 'status': 'INVALID_ARGUMENT'}}",
                "status_code": None,
            },
            "structured_output_should_call_tool_scenario:strict-or-tool:gemini-2.0-flash": {
                "type": "raw_content",
                "content": [
                    ToolCall(id="<unknown>", name="available_books", args="{}")
                ],
            },
            "structured_output_should_call_tool_scenario:strict-or-json:gemini-2.0-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "Title",
                    "author": "Author",
                    "vibe": "intruiging!",
                },
            },
            "structured_output_should_call_tool_scenario:strict:gemini-2.0-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "The Midnight Hour",
                    "author": "Benjamin Ashwood",
                    "vibe": "mysterious",
                },
            },
            "structured_output_should_call_tool_scenario:tool:gemini-2.0-flash": {
                "type": "raw_content",
                "content": [
                    ToolCall(id="<unknown>", name="available_books", args="{}")
                ],
            },
            "structured_output_should_call_tool_scenario:json:gemini-2.0-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "The Hobbit",
                    "author": "J.R.R. Tolkien",
                    "vibe": "intruiging!",
                },
            },
            "structured_output_uses_tool_output_scenario:strict-or-tool:gemini-2.5-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "Wild Seed",
                    "author": "Octavia Butler",
                    "vibe": "intriguing!",
                },
            },
            "structured_output_uses_tool_output_scenario:strict-or-json:gemini-2.5-flash": {
                "type": "exception",
                "exception_type": "ClientError",
                "exception_message": "400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': \"Function calling with a response mime type: 'application/json' is unsupported\", 'status': 'INVALID_ARGUMENT'}}",
                "status_code": None,
            },
            "structured_output_uses_tool_output_scenario:strict:gemini-2.5-flash": {
                "type": "exception",
                "exception_type": "ClientError",
                "exception_message": "400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': \"Function calling with a response mime type: 'application/json' is unsupported\", 'status': 'INVALID_ARGUMENT'}}",
                "status_code": None,
            },
            "structured_output_uses_tool_output_scenario:tool:gemini-2.5-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "Wild Seed",
                    "author": "Octavia Butler",
                    "vibe": "mysterious!",
                },
            },
            "structured_output_uses_tool_output_scenario:json:gemini-2.5-flash": {
                "type": "exception",
                "exception_type": "ClientError",
                "exception_message": "400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': \"Function calling with a response mime type: 'application/json' is unsupported\", 'status': 'INVALID_ARGUMENT'}}",
                "status_code": None,
            },
            "structured_output_uses_tool_output_scenario:strict-or-tool:gemini-2.0-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "Wild Seed",
                    "author": "Octavia Butler",
                    "vibe": "intruiging!",
                },
            },
            "structured_output_uses_tool_output_scenario:strict-or-json:gemini-2.0-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "Wild Seed",
                    "author": "Octavia Butler",
                    "vibe": "intruiging!",
                },
            },
            "structured_output_uses_tool_output_scenario:strict:gemini-2.0-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "Wild Seed",
                    "author": "Octavia Butler",
                    "vibe": "mysterious",
                },
            },
            "structured_output_uses_tool_output_scenario:tool:gemini-2.0-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "Wild Seed",
                    "author": "Octavia Butler",
                    "vibe": "intruiging!",
                },
            },
            "structured_output_uses_tool_output_scenario:json:gemini-2.0-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "Wild Seed",
                    "author": "Octavia Butler",
                    "vibe": "intruiging!",
                },
            },
            "structured_output_with_formatting_instructions_scenario:strict-or-tool:gemini-2.5-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "THE NAME OF THE WIND",
                    "author": "PATRICK ROTHFUSS",
                    "vibe": "ABSOLUTELY ENTHRALLING AND DEEPLY MYSTERIOUS WITH A TOUCH OF MELANCHOLY AND UNPARALLELED WORLD-BUILDING THAT WILL SWALLOW YOU WHOLE!",
                },
            },
            "structured_output_with_formatting_instructions_scenario:strict-or-json:gemini-2.5-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "THE NAME OF THE WIND",
                    "author": "PATRICK ROTHFUSS",
                    "vibe": "INTRIGUING",
                },
            },
            "structured_output_with_formatting_instructions_scenario:strict:gemini-2.5-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "THE NAME OF THE WIND",
                    "author": "PATRICK ROTHFUSS",
                    "vibe": "INTRIGUING",
                },
            },
            "structured_output_with_formatting_instructions_scenario:tool:gemini-2.5-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "THE NAME OF THE WIND",
                    "author": "PATRICK ROTHFUSS",
                    "vibe": "INTRIGUING",
                },
            },
            "structured_output_with_formatting_instructions_scenario:json:gemini-2.5-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "THE NAME OF THE WIND",
                    "author": "PATRICK ROTHFUSS",
                    "vibe": "A MAGNIFICENT SAGA OF MAGIC, MUSIC, AND MYSTERY, AS A LIVING LEGEND UNRAVELS HIS OWN TUMULTUOUS PAST! IMMERSE YOURSELF IN STUNNING PROSE, UNFORGETTABLE CHARACTERS, AND A WORLD SO RICH YOU CAN ALMOST TASTE THE FIREWOOD SMOKE. GET READY TO BE UTTERLY CAPTIVATED AND BEG FOR MORE! IT'S AN ABSOLUTE MASTERPIECE!",
                },
            },
            "structured_output_with_formatting_instructions_scenario:strict-or-tool:gemini-2.0-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "The Goblin Emperor",
                    "author": "Katherine Addison",
                    "vibe": "UTTERLY HEARTWARMING AND COMFORTING!",
                },
            },
            "structured_output_with_formatting_instructions_scenario:strict-or-json:gemini-2.0-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "The Priory of the Orange Tree",
                    "author": "Samantha Shannon",
                    "vibe": "EPIC FANTASY WITH DRAGONS AND QUEENS AND MAGIC AND IT'S SO GOOD YOU WILL CRY",
                },
            },
            "structured_output_with_formatting_instructions_scenario:strict:gemini-2.0-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "Jonathan Strange & Mr Norrell",
                    "author": "Susanna Clarke",
                    "vibe": "MYSTERIOUS",
                },
            },
            "structured_output_with_formatting_instructions_scenario:tool:gemini-2.0-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "Mistborn: The Final Empire",
                    "author": "Brandon Sanderson",
                    "vibe": "euphoric",
                },
            },
            "structured_output_with_formatting_instructions_scenario:json:gemini-2.0-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "Jonathan Strange & Mr Norrell",
                    "author": "Susanna Clarke",
                    "vibe": "DARK ACADEMIA MEETS ALTERNATE HISTORY WITH A DASH OF DRY BRITISH WIT! PERFECT FOR AUTUMN DAYS AND GETTING LOST IN A BYGONE ERA INFUSED WITH FORGOTTEN MAGIC! A MUST-READ FOR FANTASY LOVERS SEEKING SOMETHING TRULY UNIQUE AND IMMERSIVE!",  # codespell:ignore wit
                },
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario:strict-or-tool:gemini-2.5-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "THE LAST UNICORN",
                    "author": "PETER S. BEAGLE",
                    "vibe": "SOUL_SEARCHING",
                },
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario:strict-or-json:gemini-2.5-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "The Last Unicorn",
                    "author": "Peter S. Beagle",
                    "vibe": "SOUL_SEARCHING",
                },
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario:strict:gemini-2.5-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "The Last Unicorn",
                    "author": "Peter S. Beagle",
                    "vibe": "PROFOUNDLY SOUL_SEARCHING, A FRAGMENTED SEARCH FOR WHAT WAS LOST, FOREVER DRAINED OF HOPE",
                },
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario:tool:gemini-2.5-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "A WIZARD OF EARTHSEA",
                    "author": "URSULA K. LE GUIN",
                    "vibe": "SOUL_SEARCHING",
                },
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario:json:gemini-2.5-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "The Blade Itself",
                    "author": "Joe Abercrombie",
                    "vibe": "A WORLD SO GRIM AND BLOOD-SOAKED, WHERE HEROES ARE FLAWED MONSTERS AND HOPE IS A CRUEL JOKE, LEAVING YOU WITH AN EXISTENTIAL EMPTINESS THAT ECHOES THE INEVITABLE DECAY OF ALL THINGS. THE CRUELTY OF FATE, THE FUTILITY OF JUSTICE, AND THE BITTER TASTE OF AMBITION'S ASHES. YOUR SOUL WILL BE CRUSHED.",
                },
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario:strict-or-tool:gemini-2.0-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "The First Law",
                    "author": "Joe Abercrombie",
                    "vibe": "GRIMDARK AND HOPELESS",
                },
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario:strict-or-json:gemini-2.0-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "The First Law",
                    "author": "Joe Abercrombie",
                    "vibe": "EXISTENTIAL DREAD!",
                },
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario:strict:gemini-2.0-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "The First Law",
                    "author": "Joe Abercrombie",
                    "vibe": "DESPAIR AND NO HOPE. NONE.",
                },
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario:tool:gemini-2.0-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "The Book of Lost Things",
                    "author": "John Connolly",
                    "vibe": "soul_searching",
                },
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario:json:gemini-2.0-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "The Book of Lost Things",
                    "author": "John Connolly",
                    "vibe": "SOUL-CRUSHING GRIEF AND THE UTTER POINTLESSNESS OF EVERYTHING. A DARK FANTASY THAT WILL MAKE YOU QUESTION YOUR VERY EXISTENCE.",
                },
            },
            "structured_output_with_nested_models_scenario:strict-or-tool:gemini-2.5-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "series_name": "The Chronicles of Eldoria",
                    "author": "Elara Vance",
                    "books": [
                        {
                            "title": "Whispers in the Ancient Forest",
                            "author": "Elara Vance",
                            "vibe": "mysterious!",
                        },
                        {
                            "title": "The Sunstone's Secret",
                            "author": "Elara Vance",
                            "vibe": "intruiging!",
                        },
                        {
                            "title": "Echoes of the Crystal Kingdom",
                            "author": "Elara Vance",
                            "vibe": "euphoric!",
                        },
                    ],
                    "book_count": 3,
                },
            },
            "structured_output_with_nested_models_scenario:strict-or-json:gemini-2.5-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "series_name": "The Lord of the Rings",
                    "author": "J.R.R. Tolkien",
                    "books": [
                        {
                            "title": "The Fellowship of the Ring",
                            "author": "J.R.R. Tolkien",
                            "vibe": "intruiging!",
                        },
                        {
                            "title": "The Two Towers",
                            "author": "J.R.R. Tolkien",
                            "vibe": "mysterious!",
                        },
                        {
                            "title": "The Return of the King",
                            "author": "J.R.R. Tolkien",
                            "vibe": "euphoric!",
                        },
                    ],
                    "book_count": 3,
                },
            },
            "structured_output_with_nested_models_scenario:strict:gemini-2.5-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "series_name": "The Lord of the Rings",
                    "author": "J.R.R. Tolkien",
                    "books": [
                        {
                            "title": "The Fellowship of the Ring",
                            "author": "J.R.R. Tolkien",
                            "vibe": "intruiging!",
                        },
                        {
                            "title": "The Two Towers",
                            "author": "J.R.R. Tolkien",
                            "vibe": "soul_searching!",
                        },
                        {
                            "title": "The Return of the King",
                            "author": "J.R.R. Tolkien",
                            "vibe": "euphoric!",
                        },
                    ],
                    "book_count": 3,
                },
            },
            "structured_output_with_nested_models_scenario:tool:gemini-2.5-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "series_name": "The Lord of the Rings",
                    "author": "J.R.R. Tolkien",
                    "books": [
                        {
                            "title": "The Fellowship of the Ring",
                            "author": "J.R.R. Tolkien",
                            "vibe": "intriguing!",
                        },
                        {
                            "title": "The Two Towers",
                            "author": "J.R.R. Tolkien",
                            "vibe": "mysterious!",
                        },
                        {
                            "title": "The Return of the King",
                            "author": "J.R.R. Tolkien",
                            "vibe": "euphoric!",
                        },
                    ],
                    "book_count": 3,
                },
            },
            "structured_output_with_nested_models_scenario:json:gemini-2.5-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "series_name": "The Lord of the Rings",
                    "author": "J.R.R. Tolkien",
                    "books": [
                        {
                            "title": "The Fellowship of the Ring",
                            "author": "J.R.R. Tolkien",
                            "vibe": "intriguing!",
                        },
                        {
                            "title": "The Two Towers",
                            "author": "J.R.R. Tolkien",
                            "vibe": "mysterious!",
                        },
                        {
                            "title": "The Return of the King",
                            "author": "J.R.R. Tolkien",
                            "vibe": "euphoric!",
                        },
                    ],
                    "book_count": 3,
                },
            },
            "structured_output_with_nested_models_scenario:strict-or-tool:gemini-2.0-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "series_name": "The Aubrey–Maturin series",
                    "author": "Patrick O'Brian",
                    "books": [
                        {
                            "title": "Master and Commander",
                            "author": "Patrick O'Brian",
                            "vibe": "intruiging",
                        },
                        {
                            "title": "Post Captain",
                            "author": "Patrick O'Brian",
                            "vibe": "intruiging",
                        },
                        {
                            "title": "HMS Surprise",
                            "author": "Patrick O'Brian",
                            "vibe": "intruiging",
                        },
                        {
                            "title": "The Mauritius Command",
                            "author": "Patrick O'Brian",
                            "vibe": "intruiging",
                        },
                        {
                            "title": "Desolation Island",
                            "author": "Patrick O'Brian",
                            "vibe": "intruiging",
                        },
                        {
                            "title": "The Fortune of War",
                            "author": "Patrick O'Brian",
                            "vibe": "intruiging",
                        },
                        {
                            "title": "The Surgeon's Mate",
                            "author": "Patrick O'Brian",
                            "vibe": "intruiging",
                        },
                        {
                            "title": "The Ionian Mission",
                            "author": "Patrick O'Brian",
                            "vibe": "intruiging",
                        },
                        {
                            "title": "Treason's Harbour",
                            "author": "Patrick O'Brian",
                            "vibe": "intruiging",
                        },
                        {
                            "title": "The Far Side of the World",
                            "author": "Patrick O'Brian",
                            "vibe": "intruiging",
                        },
                        {
                            "title": "The Reverse of the Medal",
                            "author": "Patrick O'Brian",
                            "vibe": "intruiging",
                        },
                        {
                            "title": "The Letter of Marque",
                            "author": "Patrick O'Brian",
                            "vibe": "intruiging",
                        },
                        {
                            "title": "The Thirteen Gun Salute",
                            "author": "Patrick O'Brian",
                            "vibe": "intruiging",
                        },
                        {
                            "title": "The Nutmeg of Consolation",
                            "author": "Patrick O'Brian",
                            "vibe": "intruiging",
                        },
                        {
                            "title": "Clarissa Oakes",
                            "author": "Patrick O'Brian",
                            "vibe": "intruiging",
                        },
                        {
                            "title": "The Wine-Dark Sea",
                            "author": "Patrick O'Brian",
                            "vibe": "intruiging",
                        },
                        {
                            "title": "The Commodore",
                            "author": "Patrick O'Brian",
                            "vibe": "intruiging",
                        },
                        {
                            "title": "The Yellow Admiral",
                            "author": "Patrick O'Brian",
                            "vibe": "intruiging",
                        },
                        {
                            "title": "The Hundred Days",
                            "author": "Patrick O'Brian",
                            "vibe": "intruiging",
                        },
                        {
                            "title": "Blue at the Mizzen",
                            "author": "Patrick O'Brian",
                            "vibe": "intruiging",
                        },
                        {
                            "title": "The Final Unfinished Voyage",
                            "author": "Patrick O'Brian",
                            "vibe": "intruiging",
                        },
                    ],
                    "book_count": 21,
                },
            },
            "structured_output_with_nested_models_scenario:strict-or-json:gemini-2.0-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "series_name": "The Witcher",
                    "author": "Andrzej Sapkowski",
                    "books": [
                        {
                            "title": "The Last Wish",
                            "author": "Andrzej Sapkowski",
                            "vibe": "intruiging",
                        },
                        {
                            "title": "Sword of Destiny",
                            "author": "Andrzej Sapkowski",
                            "vibe": "intruiging",
                        },
                        {
                            "title": "Blood of Elves",
                            "author": "Andrzej Sapkowski",
                            "vibe": "intruiging",
                        },
                        {
                            "title": "Time of Contempt",
                            "author": "Andrzej Sapkowski",
                            "vibe": "intruiging",
                        },
                        {
                            "title": "Baptism of Fire",
                            "author": "Andrzej Sapkowski",
                            "vibe": "intruiging",
                        },
                        {
                            "title": "The Tower of the Swallow",
                            "author": "Andrzej Sapkowski",
                            "vibe": "intruiging",
                        },
                        {
                            "title": "Lady of the Lake",
                            "author": "Andrzej Sapkowski",
                            "vibe": "intruiging",
                        },
                        {
                            "title": "Season of Storms",
                            "author": "Andrzej Sapkowski",
                            "vibe": "intruiging",
                        },
                    ],
                    "book_count": 8,
                },
            },
            "structured_output_with_nested_models_scenario:strict:gemini-2.0-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "series_name": "The Lunar Chronicles",
                    "author": "Marissa Meyer",
                    "books": [
                        {
                            "title": "Cinder",
                            "author": "Marissa Meyer",
                            "vibe": "intruiging",
                        },
                        {
                            "title": "Scarlet",
                            "author": "Marissa Meyer",
                            "vibe": "intruiging",
                        },
                        {
                            "title": "Cress",
                            "author": "Marissa Meyer",
                            "vibe": "intruiging",
                        },
                        {
                            "title": "Winter",
                            "author": "Marissa Meyer",
                            "vibe": "intruiging",
                        },
                    ],
                    "book_count": 4,
                },
            },
            "structured_output_with_nested_models_scenario:tool:gemini-2.0-flash": {
                "type": "raw_content",
                "content": [
                    Text(
                        text="Okay, I need some information about the book series you're interested in. Can you tell me the name of the series, the author, and the number of books in the series? If you know the titles, authors, and vibes of each book, that would be helpful too!\n"
                    )
                ],
            },
            "structured_output_with_nested_models_scenario:json:gemini-2.0-flash": {
                "type": "formatted_output",
                "model_dump": {
                    "series_name": "The Vibe Series!",
                    "author": "JSON Response",
                    "books": [
                        {
                            "title": "Mysterious Echoes",
                            "author": "A. Reader",
                            "vibe": "mysterious!",
                        },
                        {
                            "title": "Euphoric Dreamscapes",
                            "author": "B. Wright",
                            "vibe": "euphoric!",
                        },
                        {
                            "title": "Intriguing Illusions",
                            "author": "C. Author",
                            "vibe": "intruiging!",
                        },
                        {
                            "title": "Soul-Searching Journeys",
                            "author": "D. Scribbler",
                            "vibe": "soul_searching!",
                        },
                    ],
                    "book_count": 4,
                },
            },
        }
    )

    assert actual == expected[f"{scenario_id}:{format_mode}:{test_model_id}"]


def test_custom_base_url() -> None:
    """Test that custom base URL is used for API requests."""
    example_url = "https://example.com"
    with patch("mirascope.llm.clients.google.client.Client") as mock_client_class:
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance
        google_client = llm.GoogleClient(base_url=example_url)
        mock_client_class.assert_called_once()
        call_args = mock_client_class.call_args
        assert call_args.kwargs["http_options"] is not None
        assert call_args.kwargs["http_options"].base_url == example_url
        assert google_client.client is mock_client_instance


# Included in test_google_client as this triggers a google-specific edge case for coverage.
@pytest.mark.vcr()
def test_call_no_output(google_client: llm.GoogleClient) -> None:
    """Test call where assistant generates nothing."""
    messages = [
        llm.messages.system("Do not emit ANY output, terminate immediately."),
        llm.messages.user(""),
    ]
    response = google_client.call(
        model_id=TEST_MODEL_ID,
        messages=messages,
    )
    assert isinstance(response, llm.Response)
    assert utils.response_snapshot_dict(response) == snapshot(
        {
            "provider": "google",
            "model_id": "gemini-2.0-flash",
            "params": None,
            "finish_reason": llm.FinishReason.END_TURN,
            "messages": [
                llm.SystemMessage(
                    content=llm.Text(
                        text="Do not emit ANY output, terminate immediately."
                    )
                ),
                llm.UserMessage(content=[llm.Text(text="")]),
                llm.AssistantMessage(content=[]),
            ],
        }
    )
