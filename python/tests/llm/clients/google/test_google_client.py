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
    assert isinstance(response, llm.Response)

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
@pytest.mark.vcr()
def test_every_structured_mode_should_call_tool(
    google_client: llm.GoogleClient,
    format_mode: llm.formatting.FormattingMode,
    test_model_id: llm.clients.google.GoogleModelId,
    request: pytest.FixtureRequest,
) -> None:
    """Test behavior when structured formatting is enabled and the model should call a tool.

    The correct behavior is to call the available_books tool; however depending on the
    model and the formatting mode, it may fail to do so, or may throw an exception.
    """

    scenario_data = request.getfixturevalue(
        "structured_output_should_call_tool_scenario"
    )
    llm.format(scenario_data["format"], mode=format_mode)

    try:
        response = google_client.call(model_id=test_model_id, **scenario_data)
        actual = response.content
    except Exception as e:
        actual = {
            "exception_type": type(e).__name__,
            "exception_message": str(e),
            "status_code": getattr(e, "status_code", None),
        }

    expected = snapshot(
        {
            # gemini-2.5-flash is either correct (strict-or-tool, tool) or fails explicitly (strict, json, strict-or-json)
            "gemini-2.5-flash:strict-or-tool": [  # Correct
                ToolCall(id="<unknown>", name="available_books", args="{}")
            ],
            "gemini-2.5-flash:strict-or-json": {  # Obvious failure
                "exception_type": "ClientError",
                "exception_message": "400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': \"Function calling with a response mime type: 'application/json' is unsupported\", 'status': 'INVALID_ARGUMENT'}}",
                "status_code": None,
            },
            "gemini-2.5-flash:strict": {  # Obvious failure
                "exception_type": "ClientError",
                "exception_message": "400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': \"Function calling with a response mime type: 'application/json' is unsupported\", 'status': 'INVALID_ARGUMENT'}}",
                "status_code": None,
            },
            "gemini-2.5-flash:tool": [  # Correct
                ToolCall(id="<unknown>", name="available_books", args="{}")
            ],
            "gemini-2.5-flash:json": {  # Obvious failure
                "exception_type": "ClientError",
                "exception_message": "400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': \"Function calling with a response mime type: 'application/json' is unsupported\", 'status': 'INVALID_ARGUMENT'}}",
                "status_code": None,
            },
            # gemini-2.0-flash is correct for strict-or-tool and tool, gives an invented book otherwise
            "gemini-2.0-flash:strict-or-tool": [  # Correct
                ToolCall(id="<unknown>", name="available_books", args="{}")
            ],
            "gemini-2.0-flash:strict-or-json": [  # Non-obvious failure
                Text(
                    text="""\
{
  "title": "Small Miracles",
  "author": "Anne Lamott",
  "vibe": "euphoric!"
}\
"""
                )
            ],
            "gemini-2.0-flash:strict": [  # Non-obvious failure
                Text(
                    text="""\
{
  "title": "The Midnight Realm",
  "author": "Evelyn Thorne",
  "vibe": "mysterious"
}\
"""
                )
            ],
            "gemini-2.0-flash:tool": [  # Correct
                ToolCall(id="<unknown>", name="available_books", args="{}")
            ],
            "gemini-2.0-flash:json": [  # Non-obvious failure
                Text(
                    text="""\
{
  "title": "The Goblin Emperor",
  "author": "Katherine Addison",
  "vibe": "soul_searching!"
}\
"""
                )
            ],
        }
    )
    assert actual == expected[test_model_id + ":" + format_mode]


@pytest.mark.parametrize("format_mode", FORMATTING_MODES)
@pytest.mark.vcr()
def test_every_structured_mode_basic(
    google_client: llm.GoogleClient,
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

    response = google_client.call(model_id=TEST_MODEL_ID, **scenario_data)

    system_message_content = ""
    if (first_message := response.messages[0]).role == "system":
        system_message_content = first_message.content.text

    output = response.format()
    assert output is not None
    actual = {
        "system_message": system_message_content,
        "model_dump": output.model_dump(),
    }

    expected = snapshot(
        {
            "strict-or-tool": {
                "system_message": "",
                "model_dump": {
                    "title": "Jonathan Strange & Mr Norrell",
                    "author": "Susanna Clarke",
                    "vibe": "mysterious",
                },
            },
            "strict-or-json": {
                "system_message": "",
                "model_dump": {
                    "title": "Jonathan Strange & Mr Norrell",
                    "author": "Susanna Clarke",
                    "vibe": "mysterious",
                },
            },
            "strict": {
                "system_message": "",
                "model_dump": {
                    "title": "Jonathan Strange & Mr Norrell",
                    "author": "Susanna Clarke",
                    "vibe": "intruiging",
                },
            },
            "tool": {
                "system_message": """\
When you are ready to respond to the user, call the __mirascope_formatted_output_tool__ tool to output a structured response.
Do NOT output any text in addition to the tool call.\
""",
                "model_dump": {
                    "title": "The Midnight Library",
                    "author": "Matt Haig",
                    "vibe": "soul_searching!",
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
}\
""",
                "model_dump": {
                    "title": "Mistborn: The Final Empire",
                    "author": "Brandon Sanderson",
                    "vibe": "intruiging!",
                },
            },
        }
    )
    assert actual == expected[format_mode]


@pytest.mark.parametrize("format_mode", FORMATTING_MODES)
@pytest.mark.vcr()
def test_every_structured_mode_with_instructions_and_system_message(
    google_client: llm.GoogleClient,
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

    response = google_client.call(model_id=TEST_MODEL_ID, **scenario_data)

    system_message_content = ""
    if (first_message := response.messages[0]).role == "system":
        system_message_content = first_message.content.text

    output = response.format()
    assert output is not None
    actual = {
        "system_message": system_message_content,
        "model_dump": output.model_dump(),
    }

    expected = snapshot(
        {
            "strict-or-tool": {
                "system_message": """\
You are a depressive LLM that only recommends sad books.
Pretty please output a book recommendation in JSON form.
It should have the format {title: str, author: str, vibe: str}.
Be super vibe-y with the vibe and make sure EVERYTHING IS CAPS to convey
the STRENGTH OF YOUR RECOMMENDATION!\
""",
                "model_dump": {
                    "title": "The First Law",
                    "author": "Joe Abercrombie",
                    "vibe": "GRIMDARK AND JOYLESS, JUST LIKE LIFE!",
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
                    "title": "The First Law",
                    "author": "Joe Abercrombie",
                    "vibe": "DEATH AWAITS YOU ALL. READ IT AND WEEP!",
                },
            },
            "strict": {
                "system_message": """\
You are a depressive LLM that only recommends sad books.
Pretty please output a book recommendation in JSON form.
It should have the format {title: str, author: str, vibe: str}.
Be super vibe-y with the vibe and make sure EVERYTHING IS CAPS to convey
the STRENGTH OF YOUR RECOMMENDATION!\
""",
                "model_dump": {
                    "title": "The First Law",
                    "author": "Joe Abercrombie",
                    "vibe": "EXISTENTIAL DREAD!",
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
                    "title": "The Book of Lost Things",
                    "author": "John Connolly",
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
                    "title": "The First Law",
                    "author": "Joe Abercrombie",
                    "vibe": "A GRIMDARK PIT OF DESPAIR WHERE EVERYONE IS A TERRIBLE PERSON AND EVERYTHING GOES WRONG! UTTER NIHILISM AND FUTILITY AWAIT!",
                },
            },
        }
    )
    assert actual == expected[format_mode]


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
