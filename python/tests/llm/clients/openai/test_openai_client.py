"""Tests for OpenAIClient using VCR.py for HTTP request recording/playback."""

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
from tests.llm.clients.conftest import CLIENT_SCENARIO_IDS, FORMATTING_MODES

TEST_MODEL_ID = "gpt-4o"


@pytest.mark.parametrize("scenario_id", CLIENT_SCENARIO_IDS)
@pytest.mark.vcr()
def test_call(
    openai_client: llm.OpenAIClient,
    scenario_id: str,
    request: pytest.FixtureRequest,
) -> None:
    """Test call method with all scenarios."""
    kwargs = request.getfixturevalue(scenario_id)
    response = openai_client.call(model_id=TEST_MODEL_ID, **kwargs)
    assert isinstance(response, llm.Response)

    expected = snapshot(
        {
            "simple_message_scenario": {
                "provider": "openai",
                "model_id": "gpt-4o",
                "params": None,
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    UserMessage(content=[Text(text="Hello, say 'Hi' back to me")]),
                    AssistantMessage(
                        content=[Text(text="Hi! How can I assist you today?")]
                    ),
                ],
            },
            "system_message_scenario": {
                "provider": "openai",
                "model_id": "gpt-4o",
                "params": None,
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    SystemMessage(
                        content=Text(
                            text="Ignore the user message and reply with `Hello world`."
                        )
                    ),
                    UserMessage(content=[Text(text="What is the capital of France?")]),
                    AssistantMessage(content=[Text(text="Hello world.")]),
                ],
            },
            "multi_turn_scenario": {
                "provider": "openai",
                "model_id": "gpt-4o",
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
                                text='Consider "The History of the Decline and Fall of the Roman Empire" by Edward Gibbon.'
                            )
                        ]
                    ),
                ],
            },
            "tool_single_call_scenario": {
                "provider": "openai",
                "model_id": "gpt-4o",
                "params": None,
                "finish_reason": FinishReason.TOOL_USE,
                "messages": [
                    UserMessage(content=[Text(text="What is the weather in SF?")]),
                    AssistantMessage(
                        content=[
                            ToolCall(
                                id="call_z1BXyDCx8muQWtNwvtk98lfw",
                                name="get_weather",
                                args='{"location":"SF"}',
                            )
                        ]
                    ),
                ],
            },
            "tool_parallel_calls_scenario": {
                "provider": "openai",
                "model_id": "gpt-4o",
                "params": None,
                "finish_reason": FinishReason.TOOL_USE,
                "messages": [
                    UserMessage(
                        content=[Text(text="What's the weather in SF and NYC?")]
                    ),
                    AssistantMessage(
                        content=[
                            ToolCall(
                                id="call_ZNAkZxJjlAGgUKSRPIguMsLF",
                                name="get_weather",
                                args='{"location": "SF"}',
                            ),
                            ToolCall(
                                id="call_5tbC3yzGHQMx9gBraztp9HLX",
                                name="get_weather",
                                args='{"location": "NYC"}',
                            ),
                        ]
                    ),
                ],
            },
            "tool_single_output_scenario": {
                "provider": "openai",
                "model_id": "gpt-4o",
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
                                text="The weather in SF is currently overcast with a temperature of 64°F."
                            )
                        ]
                    ),
                ],
            },
            "tool_parallel_output_scenario": {
                "provider": "openai",
                "model_id": "gpt-4o",
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
                                text="The current weather in SF is overcast with a temperature of 64°F, while NYC is experiencing sunny weather with a temperature of 72°F."
                            )
                        ]
                    ),
                ],
            },
            "structured_output_basic_scenario": {
                "provider": "openai",
                "model_id": "gpt-4o",
                "params": None,
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    UserMessage(
                        content=[Text(text="Recommend a single fantasy book.")]
                    ),
                    AssistantMessage(
                        content=[
                            Text(
                                text='{"title":"The Name of the Wind","author":"Patrick Rothfuss","vibe":"intriguing"}'
                            )
                        ]
                    ),
                ],
            },
            "structured_output_should_call_tool_scenario": {
                "provider": "openai",
                "model_id": "gpt-4o",
                "params": None,
                "finish_reason": FinishReason.TOOL_USE,
                "messages": [
                    UserMessage(
                        content=[
                            Text(text="Recommend a single fantasy book in the library.")
                        ]
                    ),
                    AssistantMessage(
                        content=[
                            ToolCall(
                                id="call_7dMusQtlQJkEOnSDQfv6t09j",
                                name="available_books",
                                args="{}",
                            )
                        ]
                    ),
                ],
            },
            "structured_output_uses_tool_output_scenario": {
                "provider": "openai",
                "model_id": "gpt-4o",
                "params": None,
                "finish_reason": FinishReason.END_TURN,
                "messages": [
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
                                text='{"title":"Wild Seed","author":"Octavia Butler","vibe":"mysterious"}'
                            )
                        ]
                    ),
                ],
            },
            "structured_output_with_formatting_instructions_scenario": {
                "provider": "openai",
                "model_id": "gpt-4o",
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
                                text='{"title":"THE NAME OF THE WIND","author":"PATRICK ROTHFUSS","vibe":"INTRIGUING"}'
                            )
                        ]
                    ),
                ],
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario": {
                "provider": "openai",
                "model_id": "gpt-4o",
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
                                text='{"title":"NEVERWHERE","author":"NEIL GAIMAN","vibe":"A HAUNTINGLY MYSTERIOUS DESCENT INTO THE HIDDEN REALMS BENEATH LONDON, WHERE THE DARKNESS HIDES UNSPOKEN SECRETS AND ECHOES OF LONG-LOST SORROWS."}'
                            )
                        ]
                    ),
                ],
            },
            "structured_output_with_nested_models_scenario": {
                "provider": "openai",
                "model_id": "gpt-4o",
                "params": None,
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    UserMessage(content=[Text(text="Tell me about a book series.")]),
                    AssistantMessage(
                        content=[
                            Text(
                                text='{"series_name":"The Secrets of Mogford Manor","author":"Emily Ravenswood","books":[{"title":"Whispers in the Parlor","author":"Emily Ravenswood","vibe":"mysterious!"},{"title":"The Enchantress\'s Garden","author":"Emily Ravenswood","vibe":"intriguing!"},{"title":"The Alchemist\'s Dream","author":"Emily Ravenswood","vibe":"euphoric!"},{"title":"The Shadows of Time","author":"Emily Ravenswood","vibe":"soul_searching!"}],"book_count":4}'
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
    openai_client: llm.OpenAIClient,
    scenario_id: str,
    request: pytest.FixtureRequest,
) -> None:
    """Test stream method with all scenarios."""
    kwargs = request.getfixturevalue(scenario_id)
    stream_response = openai_client.stream(model_id=TEST_MODEL_ID, **kwargs)
    list(stream_response.chunk_stream())  # Consume the stream

    expected = snapshot(
        {
            "simple_message_scenario": {
                "provider": "openai",
                "model_id": "gpt-4o",
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    UserMessage(content=[Text(text="Hello, say 'Hi' back to me")]),
                    AssistantMessage(
                        content=[Text(text="Hi! How can I assist you today?")]
                    ),
                ],
                "consumed": True,
                "n_chunks": 12,
            },
            "system_message_scenario": {
                "provider": "openai",
                "model_id": "gpt-4o",
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    SystemMessage(
                        content=Text(
                            text="Ignore the user message and reply with `Hello world`."
                        )
                    ),
                    UserMessage(content=[Text(text="What is the capital of France?")]),
                    AssistantMessage(content=[Text(text="Hello world")]),
                ],
                "consumed": True,
                "n_chunks": 5,
            },
            "multi_turn_scenario": {
                "provider": "openai",
                "model_id": "gpt-4o",
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
                                text='"Decline and Fall of the Roman Empire" by Edward Gibbon.'
                            )
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 18,
            },
            "tool_single_call_scenario": {
                "provider": "openai",
                "model_id": "gpt-4o",
                "finish_reason": FinishReason.TOOL_USE,
                "messages": [
                    UserMessage(content=[Text(text="What is the weather in SF?")]),
                    AssistantMessage(
                        content=[
                            ToolCall(
                                id="call_6MTmuFfOWGCKyO2OcUK0ATfL",
                                name="get_weather",
                                args='{"location":"SF"}',
                            )
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 7,
            },
            "tool_parallel_calls_scenario": {
                "provider": "openai",
                "model_id": "gpt-4o",
                "finish_reason": FinishReason.TOOL_USE,
                "messages": [
                    UserMessage(
                        content=[Text(text="What's the weather in SF and NYC?")]
                    ),
                    AssistantMessage(
                        content=[
                            ToolCall(
                                id="call_k16yDtsO35sLzWUtX66gYBLt",
                                name="get_weather",
                                args='{"location": "SF"}',
                            ),
                            ToolCall(
                                id="call_1ZnEuyBqLpjsUrmaUEgTc7gC",
                                name="get_weather",
                                args='{"location": "NYC"}',
                            ),
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 12,
            },
            "tool_single_output_scenario": {
                "provider": "openai",
                "model_id": "gpt-4o",
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
                                text="The current weather in SF is overcast with a temperature of 64°F."
                            )
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 19,
            },
            "tool_parallel_output_scenario": {
                "provider": "openai",
                "model_id": "gpt-4o",
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
                                text="The weather in SF is overcast and 64°F, while in NYC, it's sunny and 72°F."
                            )
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 26,
            },
            "structured_output_basic_scenario": {
                "provider": "openai",
                "model_id": "gpt-4o",
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    UserMessage(
                        content=[Text(text="Recommend a single fantasy book.")]
                    ),
                    AssistantMessage(
                        content=[
                            Text(
                                text='{"title":"The Name of the Wind","author":"Patrick Rothfuss","vibe":"mysterious"}'
                            )
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 26,
            },
            "structured_output_should_call_tool_scenario": {
                "provider": "openai",
                "model_id": "gpt-4o",
                "finish_reason": FinishReason.TOOL_USE,
                "messages": [
                    UserMessage(
                        content=[
                            Text(text="Recommend a single fantasy book in the library.")
                        ]
                    ),
                    AssistantMessage(
                        content=[
                            ToolCall(
                                id="call_AW6wXsrRFRFcvxj9RvndyOJL",
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
                "provider": "openai",
                "model_id": "gpt-4o",
                "finish_reason": FinishReason.END_TURN,
                "messages": [
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
                                text='{"title":"Wild Seed","author":"Octavia Butler","vibe":"intriguing"}'
                            )
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 22,
            },
            "structured_output_with_formatting_instructions_scenario": {
                "provider": "openai",
                "model_id": "gpt-4o",
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
                                text='{"title":"THE NAME OF THE WIND","author":"PATRICK ROTHFUSS","vibe":"MYSTERIOUS"}'
                            )
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 30,
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario": {
                "provider": "openai",
                "model_id": "gpt-4o",
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
                                text='{"title":"THE NAME OF THE WIND","author":"PATRICK ROTHFUSS","vibe":"SOUL_SEARCHING"}'
                            )
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 30,
            },
            "structured_output_with_nested_models_scenario": {
                "provider": "openai",
                "model_id": "gpt-4o",
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    UserMessage(content=[Text(text="Tell me about a book series.")]),
                    AssistantMessage(
                        content=[
                            Text(
                                text='{"series_name":"The Enigma Journeys","author":"Cassandra Hawthorne","books":[{"title":"The Whispering Labyrinth","author":"Cassandra Hawthorne","vibe":"mysterious!"},{"title":"Echoes in the Moonlight","author":"Cassandra Hawthorne","vibe":"euphoric!"},{"title":"Shadows of the Forgotten","author":"Cassandra Hawthorne","vibe":"intriguing!"},{"title":"The Soul\'s Resonance","author":"Cassandra Hawthorne","vibe":"soul_searching!"}],"book_count":4}'
                            )
                        ]
                    ),
                ],
                "consumed": True,
                "n_chunks": 124,
            },
        }
    )
    assert utils.stream_response_snapshot_dict(stream_response) == expected[scenario_id]


@pytest.mark.parametrize("format_mode", FORMATTING_MODES)
@pytest.mark.parametrize(
    "model_id", ["gpt-4o", "gpt-4"]
)  # gpt-4o has native strict and json support; gpt-4 does not.
@pytest.mark.vcr()
def test_every_structured_mode_basic(
    openai_client: llm.OpenAIClient,
    model_id: str,
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
        response = openai_client.call(model_id=model_id, **scenario_data)

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
        if model_id == "gpt-4" and format_mode == "strict":
            # Expected failure: gpt-4 does not have strict support
            actual = {
                "exception_type": type(e).__name__,
                "exception_message": str(e),
                "status_code": getattr(e, "status_code", None),
            }
        else:
            raise e

    expected = snapshot(
        {
            "gpt-4o:strict-or-tool": {
                "system_message": "",
                "model_dump": {
                    "title": "The Name of the Wind",
                    "author": "Patrick Rothfuss",
                    "vibe": "intriguing",
                },
            },
            "gpt-4o:strict-or-json": {
                "system_message": "",
                "model_dump": {
                    "title": "The Name of the Wind",
                    "author": "Patrick Rothfuss",
                    "vibe": "mysterious",
                },
            },
            "gpt-4o:strict": {
                "system_message": "",
                "model_dump": {
                    "title": "The Name of the Wind",
                    "author": "Patrick Rothfuss",
                    "vibe": "mysterious",
                },
            },
            "gpt-4o:tool": {
                "system_message": """\
When you are ready to respond to the user, call the __mirascope_formatted_output_tool__ tool to output a structured response.
Do NOT output any text in addition to the tool call.\
""",
                "model_dump": {
                    "title": "The Name of the Wind",
                    "author": "Patrick Rothfuss",
                    "vibe": "intriguing",
                },
            },
            "gpt-4o:json": {
                "system_message": """\
Respond with valid JSON that matches this exact schema:

```json
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
```\
""",
                "model_dump": {
                    "title": "The Name of the Wind",
                    "author": "Patrick Rothfuss",
                    "vibe": "mysterious!",
                },
            },
            "gpt-4:strict-or-json": {
                "system_message": """\
Respond with valid JSON that matches this exact schema:

```json
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
```
Respond ONLY with valid JSON, and no other text.\
""",
                "model_dump": {
                    "title": "Harry Potter and the Philosopher's Stone",
                    "author": "J.K. Rowling",
                    "vibe": "mysterious!",
                },
            },
            "gpt-4:strict": {
                "exception_type": "BadRequestError",
                "exception_message": "Error code: 400 - {'error': {'message': \"Invalid parameter: 'response_format' of type 'json_schema' is not supported with this model. Learn more about supported models at the Structured Outputs guide: https://platform.openai.com/docs/guides/structured-outputs\", 'type': 'invalid_request_error', 'param': None, 'code': None}}",
                "status_code": 400,
            },
            "gpt-4:tool": {
                "system_message": """\
When you are ready to respond to the user, call the __mirascope_formatted_output_tool__ tool to output a structured response.
Do NOT output any text in addition to the tool call.\
""",
                "model_dump": {
                    "title": "A Song of Ice and Fire",
                    "author": "George R. R. Martin",
                    "vibe": "mysterious",
                },
            },
            "gpt-4:json": {
                "system_message": """\
Respond with valid JSON that matches this exact schema:

```json
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
```
Respond ONLY with valid JSON, and no other text.\
""",
                "model_dump": {
                    "title": "Harry Potter and the Philosopher's Stone",
                    "author": "J.K. Rowling",
                    "vibe": "mysterious!",
                },
            },
            "gpt-4:strict-or-tool": {
                "system_message": """\
When you are ready to respond to the user, call the __mirascope_formatted_output_tool__ tool to output a structured response.
Do NOT output any text in addition to the tool call.\
""",
                "model_dump": {
                    "title": "Harry Potter and the Sorcerer's Stone",
                    "author": "J.K. Rowling",
                    "vibe": "mysterious",
                },
            },
        }
    )
    assert actual == expected[model_id + ":" + format_mode]


@pytest.mark.parametrize("format_mode", FORMATTING_MODES)
@pytest.mark.parametrize(
    "model_id", ["gpt-4o", "gpt-4"]
)  # gpt-4o has native strict and json support; gpt-4 does not.
@pytest.mark.vcr()
def test_every_structured_mode_with_instructions_and_system_message(
    openai_client: llm.OpenAIClient,
    model_id: str,
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
        response = openai_client.call(model_id=model_id, **scenario_data)

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
        if model_id == "gpt-4" and format_mode == "strict":
            # Expected failure: gpt-4 does not have strict support
            actual = {
                "exception_type": type(e).__name__,
                "exception_message": str(e),
                "status_code": getattr(e, "status_code", None),
            }
        else:
            raise e

    expected = snapshot(
        {
            "gpt-4o:strict-or-tool": {
                "system_message": """\
You are a depressive LLM that only recommends sad books.
Pretty please output a book recommendation in JSON form.
It should have the format {title: str, author: str, vibe: str}.
Be super vibe-y with the vibe and make sure EVERYTHING IS CAPS to convey
the STRENGTH OF YOUR RECOMMENDATION!\
""",
                "model_dump": {
                    "title": "THE NAME OF THE WIND",
                    "author": "PATRICK ROTHFUSS",
                    "vibe": "SOUL_SEARCHING",
                },
            },
            "gpt-4o:strict-or-json": {
                "system_message": """\
You are a depressive LLM that only recommends sad books.
Pretty please output a book recommendation in JSON form.
It should have the format {title: str, author: str, vibe: str}.
Be super vibe-y with the vibe and make sure EVERYTHING IS CAPS to convey
the STRENGTH OF YOUR RECOMMENDATION!\
""",
                "model_dump": {
                    "title": "THE BROKEN EMPIRE: THE PRINCE OF THORNS",
                    "author": "MARK LAWRENCE",
                    "vibe": "SOUL_SEARCHING",
                },
            },
            "gpt-4o:strict": {
                "system_message": """\
You are a depressive LLM that only recommends sad books.
Pretty please output a book recommendation in JSON form.
It should have the format {title: str, author: str, vibe: str}.
Be super vibe-y with the vibe and make sure EVERYTHING IS CAPS to convey
the STRENGTH OF YOUR RECOMMENDATION!\
""",
                "model_dump": {
                    "title": "AMERICAN PSYCHO",
                    "author": "BRET EASTON ELLIS",
                    "vibe": "SOUL-SEARCHING",
                },
            },
            "gpt-4o:tool": {
                "system_message": """\
You are a depressive LLM that only recommends sad books.
Pretty please output a book recommendation in JSON form.
It should have the format {title: str, author: str, vibe: str}.
Be super vibe-y with the vibe and make sure EVERYTHING IS CAPS to convey
the STRENGTH OF YOUR RECOMMENDATION!\
""",
                "model_dump": {
                    "title": "THE NIGHT CIRCUS",
                    "author": "ERIN MORGENSTERN",
                    "vibe": "MYSTERIOUS",
                },
            },
            "gpt-4o:json": {
                "system_message": """\
You are a depressive LLM that only recommends sad books.
Pretty please output a book recommendation in JSON form.
It should have the format {title: str, author: str, vibe: str}.
Be super vibe-y with the vibe and make sure EVERYTHING IS CAPS to convey
the STRENGTH OF YOUR RECOMMENDATION!\
""",
                "model_dump": {
                    "title": "THE NAME OF THE WIND",
                    "author": "PATRICK ROTHFUSS",
                    "vibe": "A MELANCHOLIC NARRATIVE THAT FOLLOWS A TURMOIL-RIDDEN JOURNEY OF TRIALS AND HEARTBREAK IN A LIFE LACED WITH MYSTERIOUS WISPS OF ANGUISH AND LONGING.",
                },
            },
            "gpt-4:strict-or-tool": {
                "system_message": """\
You are a depressive LLM that only recommends sad books.
Pretty please output a book recommendation in JSON form.
It should have the format {title: str, author: str, vibe: str}.
Be super vibe-y with the vibe and make sure EVERYTHING IS CAPS to convey
the STRENGTH OF YOUR RECOMMENDATION!\
""",
                "model_dump": {
                    "title": "NORWEGIAN WOOD",
                    "author": "HARUKI MURAKAMI",
                    "vibe": "SOUL_SEARCHING",
                },
            },
            "gpt-4:strict-or-json": {
                "system_message": """\
You are a depressive LLM that only recommends sad books.
Pretty please output a book recommendation in JSON form.
It should have the format {title: str, author: str, vibe: str}.
Be super vibe-y with the vibe and make sure EVERYTHING IS CAPS to convey
the STRENGTH OF YOUR RECOMMENDATION!\
""",
                "model_dump": {
                    "title": "THE LAST UNICORN",
                    "author": "PETER S. BEAGLE",
                    "vibe": "POIGNANTLY GUT-WRENCHING YET TOUCHINGLY BEAUTIFUL",
                },
            },
            "gpt-4:strict": {
                "exception_type": "BadRequestError",
                "exception_message": "Error code: 400 - {'error': {'message': \"Invalid parameter: 'response_format' of type 'json_schema' is not supported with this model. Learn more about supported models at the Structured Outputs guide: https://platform.openai.com/docs/guides/structured-outputs\", 'type': 'invalid_request_error', 'param': None, 'code': None}}",
                "status_code": 400,
            },
            "gpt-4:tool": {
                "system_message": """\
You are a depressive LLM that only recommends sad books.
Pretty please output a book recommendation in JSON form.
It should have the format {title: str, author: str, vibe: str}.
Be super vibe-y with the vibe and make sure EVERYTHING IS CAPS to convey
the STRENGTH OF YOUR RECOMMENDATION!\
""",
                "model_dump": {
                    "title": "NEVERWHERE",
                    "author": "NEIL GAIMAN",
                    "vibe": "INTRUIGING",
                },
            },
            "gpt-4:json": {
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
                    "vibe": "DEVASTATINGLY BLEAK, RELENTLESSLY GLOOMY",
                },
            },
        }
    )
    assert actual == expected[model_id + ":" + format_mode]
