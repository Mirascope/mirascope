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
from tests.llm.clients.conftest import (
    CLIENT_SCENARIO_IDS,
    FORMATTING_MODES,
    STRUCTURED_SCENARIO_IDS,
)

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
@pytest.mark.parametrize("test_model_id", ["gpt-4o", "gpt-4"])
@pytest.mark.parametrize("scenario_id", STRUCTURED_SCENARIO_IDS)
@pytest.mark.vcr()
def test_structured_output_all_scenarios(
    openai_client: llm.OpenAIClient,
    test_model_id: str,
    format_mode: llm.formatting.FormattingMode,
    scenario_id: str,
    request: pytest.FixtureRequest,
) -> None:
    """Test all structured output scenarios across all formatting modes."""
    scenario_data = request.getfixturevalue(scenario_id)
    llm.format(scenario_data["format"], mode=format_mode)

    try:
        response = openai_client.call(model_id=test_model_id, **scenario_data)

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
            "structured_output_basic_scenario:strict-or-tool:gpt-4o": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "The Name of the Wind",
                    "author": "Patrick Rothfuss",
                    "vibe": "euphoric",
                },
            },
            "structured_output_basic_scenario:strict-or-json:gpt-4o": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "The Night Circus",
                    "author": "Erin Morgenstern",
                    "vibe": "mysterious",
                },
            },
            "structured_output_basic_scenario:strict:gpt-4o": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "The Name of the Wind",
                    "author": "Patrick Rothfuss",
                    "vibe": "intriguing",
                },
            },
            "structured_output_basic_scenario:tool:gpt-4o": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "The Name of the Wind",
                    "author": "Patrick Rothfuss",
                    "vibe": "mysterious",
                },
            },
            "structured_output_basic_scenario:json:gpt-4o": {
                "type": "raw_content",
                "content": [
                    Text(
                        text="""\
{
  "description": "A book recommendation with metadata. ALWAYS add an exclamation point to the vibe!",
  "properties": {
    "title": "The Name of the Wind",
    "author": "Patrick Rothfuss",
    "vibe": "Intruiging!"
  },
  "required": [
    "title",
    "author",
    "vibe"
  ],
  "title": "Book",
  "type": "object"
}\
"""
                    )
                ],
            },
            "structured_output_basic_scenario:strict-or-tool:gpt-4": {
                "type": "raw_content",
                "content": [
                    ToolCall(
                        id="call_JaamJzeDwbnn3pFh3ZdHdhct",
                        name='__mirascope_formatted_output_tool__["assistant',
                        args="""\
{
"title": "Harry Potter and the Sorcerer's Stone",
"author": "J.K. Rowling",
"vibe": "mysterious"
}\
""",
                    )
                ],
            },
            "structured_output_basic_scenario:strict-or-json:gpt-4": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "Harry Potter and the Philosopher's Stone",
                    "author": "J.K. Rowling",
                    "vibe": "mysterious!",
                },
            },
            "structured_output_basic_scenario:strict:gpt-4": {
                "type": "exception",
                "exception_type": "BadRequestError",
                "exception_message": "Error code: 400 - {'error': {'message': \"Invalid parameter: 'response_format' of type 'json_schema' is not supported with this model. Learn more about supported models at the Structured Outputs guide: https://platform.openai.com/docs/guides/structured-outputs\", 'type': 'invalid_request_error', 'param': None, 'code': None}}",
                "status_code": 400,
            },
            "structured_output_basic_scenario:tool:gpt-4": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "Harry Potter and the Sorcerer's Stone",
                    "author": "J.K. Rowling",
                    "vibe": "mysterious",
                },
            },
            "structured_output_basic_scenario:json:gpt-4": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "Harry Potter and the Sorcerer's Stone",
                    "author": "J.K. Rowling",
                    "vibe": "mysterious!",
                },
            },
            "structured_output_should_call_tool_scenario:strict-or-tool:gpt-4o": {
                "type": "raw_content",
                "content": [
                    ToolCall(
                        id="call_cywSSU1MtusgCdvwto3eT7Vg",
                        name="available_books",
                        args="{}",
                    )
                ],
            },
            "structured_output_should_call_tool_scenario:strict-or-json:gpt-4o": {
                "type": "raw_content",
                "content": [
                    ToolCall(
                        id="call_GvgzOQsu4yuHp3bCvEUyqPLT",
                        name="available_books",
                        args="{}",
                    )
                ],
            },
            "structured_output_should_call_tool_scenario:strict:gpt-4o": {
                "type": "raw_content",
                "content": [
                    ToolCall(
                        id="call_7lKVltoZwvkaQcJPHJUBCwzA",
                        name="available_books",
                        args="{}",
                    )
                ],
            },
            "structured_output_should_call_tool_scenario:tool:gpt-4o": {
                "type": "raw_content",
                "content": [
                    ToolCall(
                        id="call_QGjBzF0Y2Jji5p55SxpfoGOR",
                        name="available_books",
                        args="{}",
                    )
                ],
            },
            "structured_output_should_call_tool_scenario:json:gpt-4o": {
                "type": "raw_content",
                "content": [
                    ToolCall(
                        id="call_bWkrqHJcHqPX1BTgdCeOA83i",
                        name="available_books",
                        args="{}",
                    )
                ],
            },
            "structured_output_should_call_tool_scenario:strict-or-tool:gpt-4": {
                "type": "raw_content",
                "content": [
                    ToolCall(
                        id="call_QJBWKGvk0yFroq3cFhFVO4jf",
                        name="available_books",
                        args="{}",
                    )
                ],
            },
            "structured_output_should_call_tool_scenario:strict-or-json:gpt-4": {
                "type": "raw_content",
                "content": [
                    Text(
                        text="""\
Sorry, as an AI, I cannot browse a library or perform actions. I can only provide example JSON data based on the provided schema. Here is a hypothetical example:

{
  "title": "Harry Potter and the Philosopher's Stone",
  "author": "J. K. Rowling",
  "vibe": "mysterious!"
}\
"""
                    )
                ],
            },
            "structured_output_should_call_tool_scenario:strict:gpt-4": {
                "type": "exception",
                "exception_type": "BadRequestError",
                "exception_message": "Error code: 400 - {'error': {'message': \"Invalid parameter: 'response_format' of type 'json_schema' is not supported with this model. Learn more about supported models at the Structured Outputs guide: https://platform.openai.com/docs/guides/structured-outputs\", 'type': 'invalid_request_error', 'param': None, 'code': None}}",
                "status_code": 400,
            },
            "structured_output_should_call_tool_scenario:tool:gpt-4": {
                "type": "raw_content",
                "content": [
                    ToolCall(
                        id="call_rq6RcLW50UeUcHuAEwtZRJEz",
                        name="available_books",
                        args="{}",
                    )
                ],
            },
            "structured_output_should_call_tool_scenario:json:gpt-4": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "Harry Potter and the Philosopher's Stone",
                    "author": "J.K. Rowling",
                    "vibe": "mysterious!",
                },
            },
            "structured_output_uses_tool_output_scenario:strict-or-tool:gpt-4o": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "The Long Way to a Small Angry Planet",
                    "author": "Becky Chambers",
                    "vibe": "intriguing",
                },
            },
            "structured_output_uses_tool_output_scenario:strict-or-json:gpt-4o": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "The Long Way to a Small Angry Planet",
                    "author": "Becky Chambers",
                    "vibe": "intriguing",
                },
            },
            "structured_output_uses_tool_output_scenario:strict:gpt-4o": {
                "type": "raw_content",
                "content": [
                    Text(
                        text="""\
{"title":"Wild Seed","author":"Octavia Butler","vibe":"soul_searching"}
{"title":"The Long Way to a Small Angry Planet","author":"Becky Chambers","vibe":"euphoric"}\
"""
                    )
                ],
            },
            "structured_output_uses_tool_output_scenario:tool:gpt-4o": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "Wild Seed",
                    "author": "Octavia Butler",
                    "vibe": "mysterious",
                },
            },
            "structured_output_uses_tool_output_scenario:json:gpt-4o": {
                "type": "raw_content",
                "content": [
                    Text(
                        text="""\
{
  "description": "A book recommendation with metadata. ALWAYS add an exclamation point to the vibe!",
  "properties": {
    "title": "Wild Seed",
    "author": "Octavia Butler",
    "vibe": "intriguing!"
  },
  "required": [
    "title",
    "author",
    "vibe"
  ],
  "title": "Book",
  "type": "object"
}\
"""
                    )
                ],
            },
            "structured_output_uses_tool_output_scenario:strict-or-tool:gpt-4": {
                "type": "raw_content",
                "content": [
                    ToolCall(
                        id="call_xqhqM6ZU6DElj60C1yC8HGil",
                        name='__mirascope_formatted_output_tool__["assistant',
                        args="""\
{
  "title": "Wild Seed",
  "author": "Octavia Butler",
  "vibe": "mysterious"
}\
""",
                    )
                ],
            },
            "structured_output_uses_tool_output_scenario:strict-or-json:gpt-4": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "Wild Seed",
                    "author": "Octavia Butler",
                    "vibe": "mysterious!",
                },
            },
            "structured_output_uses_tool_output_scenario:strict:gpt-4": {
                "type": "exception",
                "exception_type": "BadRequestError",
                "exception_message": "Error code: 400 - {'error': {'message': \"Invalid parameter: 'response_format' of type 'json_schema' is not supported with this model. Learn more about supported models at the Structured Outputs guide: https://platform.openai.com/docs/guides/structured-outputs\", 'type': 'invalid_request_error', 'param': None, 'code': None}}",
                "status_code": 400,
            },
            "structured_output_uses_tool_output_scenario:tool:gpt-4": {
                "type": "raw_content",
                "content": [
                    ToolCall(
                        id="call_M0hWIvdC7q0Kz9hSnw6YIU3i",
                        name="__mirascope_formatted_output_tool__.__assistant",
                        args="""\
{
"title": "Wild Seed",
"author": "Octavia Butler",
"vibe": "mysterious"
}\
""",
                    )
                ],
            },
            "structured_output_uses_tool_output_scenario:json:gpt-4": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "Wild Seed",
                    "author": "Octavia Butler",
                    "vibe": "mysterious!",
                },
            },
            "structured_output_with_formatting_instructions_scenario:strict-or-tool:gpt-4o": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "THE NAME OF THE WIND",
                    "author": "PATRICK ROTHFUSS",
                    "vibe": "ENCHANTING AND MESMERIZING",
                },
            },
            "structured_output_with_formatting_instructions_scenario:strict-or-json:gpt-4o": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "THE NAME OF THE WIND",
                    "author": "PATRICK ROTHFUSS",
                    "vibe": "MYSTERIOUS",
                },
            },
            "structured_output_with_formatting_instructions_scenario:strict:gpt-4o": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "THE NAME OF THE WIND",
                    "author": "PATRICK ROTHFUSS",
                    "vibe": "UTTERLY ENCHANTING AND MESMERIZING",
                },
            },
            "structured_output_with_formatting_instructions_scenario:tool:gpt-4o": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "THE NAME OF THE WIND",
                    "author": "PATRICK ROTHFUSS",
                    "vibe": "MYSTERIOUS",
                },
            },
            "structured_output_with_formatting_instructions_scenario:json:gpt-4o": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "THE NAME OF THE WIND",
                    "author": "PATRICK ROTHFUSS",
                    "vibe": "EPICALLY MAGICAL AND MYSTERIOUS, WITH A TOUCH OF FOLKLORIC WONDER!",
                },
            },
            "structured_output_with_formatting_instructions_scenario:strict-or-tool:gpt-4": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "GAME OF THRONES",
                    "author": "GEORGE R. R. MARTIN",
                    "vibe": "INTRUIGING",
                },
            },
            "structured_output_with_formatting_instructions_scenario:strict-or-json:gpt-4": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "THE LORD OF THE RINGS",
                    "author": "J.R.R. TOLKIEN",
                    "vibe": "EPIC FANTASY, ADVENTURE, MYSTERY, BEAUTIFULLY COMPLEX, ABSOLUTELY MAGICAL!",
                },
            },
            "structured_output_with_formatting_instructions_scenario:strict:gpt-4": {
                "type": "exception",
                "exception_type": "BadRequestError",
                "exception_message": "Error code: 400 - {'error': {'message': \"Invalid parameter: 'response_format' of type 'json_schema' is not supported with this model. Learn more about supported models at the Structured Outputs guide: https://platform.openai.com/docs/guides/structured-outputs\", 'type': 'invalid_request_error', 'param': None, 'code': None}}",
                "status_code": 400,
            },
            "structured_output_with_formatting_instructions_scenario:tool:gpt-4": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "A GAME OF THRONES",
                    "author": "GEORGE R.R. MARTIN",
                    "vibe": "INTRUIGING",
                },
            },
            "structured_output_with_formatting_instructions_scenario:json:gpt-4": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "HARRY POTTER AND THE GOBLET OF FIRE",
                    "author": "J.K. ROWLING",
                    "vibe": "MYSTICAL, ENCHANTING, EPIC! CANNOT MISS THIS ROLLER COASTER RIDE THROUGH THE WORLD OF WITCHCRAFT AND WIZARDRY!",
                },
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario:strict-or-tool:gpt-4o": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "THE SLOW REGARD OF SILENT THINGS",
                    "author": "PATRICK ROTHFUSS",
                    "vibe": "SOUL-SHATTERING SOLITUDE",
                },
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario:strict-or-json:gpt-4o": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "THE OCEAN AT THE END OF THE LANE",
                    "author": "NEIL GAIMAN",
                    "vibe": "SOUL_SEARCHING",
                },
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario:strict:gpt-4o": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "THE NIGHT CIRCUS",
                    "author": "ERIN MORGENSTERN",
                    "vibe": "MYSTERIOUS",
                },
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario:tool:gpt-4o": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "NORWEGIAN WOOD",
                    "author": "HARUKI MURAKAMI",
                    "vibe": "SOUL_SEARCHING",
                },
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario:json:gpt-4o": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "THE NAME OF THE WIND",
                    "author": "PATRICK ROTHFUSS",
                    "vibe": "A POIGNANT TALE OF LOSS AND YEARNING WRAPPED IN THE MYSTICAL VEIL OF FANTASY! HERE, MAGIC IS BEAUTIFUL BUT ALSO REMINISCENT OF ALL THAT ONE DESIRES BUT CAN NEVER TRULY GRASP! A JOURNEY OF LONGING AND NEVER-ENDING SADNESS!",
                },
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario:strict-or-tool:gpt-4": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "A GAME OF THRONES",
                    "author": "GEORGE R. R. MARTIN",
                    "vibe": "SOUL_SEARCHING",
                },
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario:strict-or-json:gpt-4": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "A GAME OF THRONES",
                    "author": "GEORGE R.R. MARTIN",
                    "vibe": "MOURNFUL, BLEAK, HEART-WRENCHING",
                },
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario:strict:gpt-4": {
                "type": "exception",
                "exception_type": "BadRequestError",
                "exception_message": "Error code: 400 - {'error': {'message': \"Invalid parameter: 'response_format' of type 'json_schema' is not supported with this model. Learn more about supported models at the Structured Outputs guide: https://platform.openai.com/docs/guides/structured-outputs\", 'type': 'invalid_request_error', 'param': None, 'code': None}}",
                "status_code": 400,
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario:tool:gpt-4": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "THE SADDEST PART OF THE ENDING",
                    "author": "RACHEL AARON",
                    "vibe": "SOUL_SEARCHING",
                },
            },
            "structured_output_with_formatting_instructions_and_system_message_scenario:json:gpt-4": {
                "type": "formatted_output",
                "model_dump": {
                    "title": "THE ROAD",
                    "author": "CORMAC MCCARTHY",
                    "vibe": "UTTERLY HEART-WRENCHING AND DESPAIRINGLY BLEAK",
                },
            },
            "structured_output_with_nested_models_scenario:strict-or-tool:gpt-4o": {
                "type": "formatted_output",
                "model_dump": {
                    "series_name": "The Dreamwalker Chronicles",
                    "author": "Elara Dawn",
                    "books": [
                        {
                            "title": "The Awakening",
                            "author": "Elara Dawn",
                            "vibe": "Mysterious!",
                        },
                        {
                            "title": "Veil of Shadows",
                            "author": "Elara Dawn",
                            "vibe": "Intriguing!",
                        },
                        {
                            "title": "Destined Paths",
                            "author": "Elara Dawn",
                            "vibe": "Soul Searching!",
                        },
                        {
                            "title": "The Final Portal",
                            "author": "Elara Dawn",
                            "vibe": "Euphoric!",
                        },
                    ],
                    "book_count": 4,
                },
            },
            "structured_output_with_nested_models_scenario:strict-or-json:gpt-4o": {
                "type": "formatted_output",
                "model_dump": {
                    "series_name": "The Quantum Realm",
                    "author": "Alden Thorne",
                    "books": [
                        {
                            "title": "The Subatomic Stranger",
                            "author": "Alden Thorne",
                            "vibe": "mysterious!",
                        },
                        {
                            "title": "Entangled Enthusiasm",
                            "author": "Alden Thorne",
                            "vibe": "euphoric!",
                        },
                        {
                            "title": "Quarks and Quandaries",
                            "author": "Alden Thorne",
                            "vibe": "intriguing!",
                        },
                        {
                            "title": "The Event Horizon",
                            "author": "Alden Thorne",
                            "vibe": "soul_searching!",
                        },
                    ],
                    "book_count": 4,
                },
            },
            "structured_output_with_nested_models_scenario:strict:gpt-4o": {
                "type": "formatted_output",
                "model_dump": {
                    "series_name": "The Enchanted Lands",
                    "author": "Elara Moonstone",
                    "books": [
                        {
                            "title": "The Whispering Forest",
                            "author": "Elara Moonstone",
                            "vibe": "Mysterious!",
                        },
                        {
                            "title": "The Luminous Lake",
                            "author": "Elara Moonstone",
                            "vibe": "Euphoric!",
                        },
                        {
                            "title": "The Secret Shadows",
                            "author": "Elara Moonstone",
                            "vibe": "Intriguing!",
                        },
                        {
                            "title": "The Soul's Journey",
                            "author": "Elara Moonstone",
                            "vibe": "Soul-searching!",
                        },
                    ],
                    "book_count": 4,
                },
            },
            "structured_output_with_nested_models_scenario:tool:gpt-4o": {
                "type": "formatted_output",
                "model_dump": {
                    "series_name": "The Chronicles of Narnia",
                    "author": "C.S. Lewis",
                    "books": [
                        {
                            "title": "The Lion, the Witch and the Wardrobe",
                            "author": "C.S. Lewis",
                            "vibe": "mysterious",
                        },
                        {
                            "title": "Prince Caspian",
                            "author": "C.S. Lewis",
                            "vibe": "intriguing",
                        },
                        {
                            "title": "The Voyage of the Dawn Treader",
                            "author": "C.S. Lewis",
                            "vibe": "euphoric",
                        },
                        {
                            "title": "The Silver Chair",
                            "author": "C.S. Lewis",
                            "vibe": "intriguing",
                        },
                        {
                            "title": "The Horse and His Boy",
                            "author": "C.S. Lewis",
                            "vibe": "mysterious",
                        },
                        {
                            "title": "The Magician's Nephew",
                            "author": "C.S. Lewis",
                            "vibe": "soul_searching",
                        },
                        {
                            "title": "The Last Battle",
                            "author": "C.S. Lewis",
                            "vibe": "mysterious",
                        },
                    ],
                    "book_count": 7,
                },
            },
            "structured_output_with_nested_models_scenario:json:gpt-4o": {
                "type": "formatted_output",
                "model_dump": {
                    "series_name": "The Kingkiller Chronicle",
                    "author": "Patrick Rothfuss",
                    "books": [
                        {
                            "title": "The Name of the Wind",
                            "author": "Patrick Rothfuss",
                            "vibe": "mysterious!",
                        },
                        {
                            "title": "The Wise Man's Fear",
                            "author": "Patrick Rothfuss",
                            "vibe": "intriguing!",
                        },
                    ],
                    "book_count": 2,
                },
            },
            "structured_output_with_nested_models_scenario:strict-or-tool:gpt-4": {
                "type": "raw_content",
                "content": [
                    ToolCall(
                        id="call_rxH4dkUPKb9cx0OiSrOeWujN",
                        name="__mirascope_formatted_output_tool__.__invoke",
                        args="""\
{
"series_name": "Harry Potter",
"author": "J.K. Rowling",
"books": [
  {
    "title": "Harry Potter and the Philosopher's Stone",
    "author": "J.K. Rowling",
    "vibe": "Fantasy"
  },
  {
    "title": "Harry Potter and the Chamber of Secrets",
    "author": "J.K. Rowling",
    "vibe": "Fantasy"
  },
  {
    "title": "Harry Potter and the Prisoner of Azkaban",
    "author": "J.K. Rowling",
    "vibe": "Fantasy"
  },
  {
    "title": "Harry Potter and the Goblet of Fire",
    "author": "J.K. Rowling",
    "vibe": "Fantasy"
  },
  {
    "title": "Harry Potter and the Order of Phoenix",
    "author": "J.K. Rowling",
    "vibe": "Fantasy"
  },
  {
    "title": "Harry Potter and the Half-Blood Prince",
    "author": "J.K. Rowling",
    "vibe": "Fantasy"
  },
  {
    "title": "Harry Potter and the Deathly Hallows",
    "author": "J.K. Rowling",
    "vibe": "Fantasy"
  }
],
"book_count": 7
}\
""",
                    )
                ],
            },
            "structured_output_with_nested_models_scenario:strict-or-json:gpt-4": {
                "type": "formatted_output",
                "model_dump": {
                    "series_name": "Harry Potter",
                    "author": "J.K. Rowling",
                    "books": [
                        {
                            "title": "Harry Potter and the Philosopher's Stone",
                            "author": "J.K. Rowling",
                            "vibe": "mysterious!",
                        },
                        {
                            "title": "Harry Potter and the Chamber of Secrets",
                            "author": "J.K. Rowling",
                            "vibe": "intruiging!",
                        },
                        {
                            "title": "Harry Potter and the Prisoner of Azkaban",
                            "author": "J.K. Rowling",
                            "vibe": "euphoric!",
                        },
                        {
                            "title": "Harry Potter and the Goblet of Fire",
                            "author": "J.K. Rowling",
                            "vibe": "soul_searching!",
                        },
                        {
                            "title": "Harry Potter and the Order of the Phoenix",
                            "author": "J.K. Rowling",
                            "vibe": "mysterious!",
                        },
                        {
                            "title": "Harry Potter and the Half-Blood Prince",
                            "author": "J.K. Rowling",
                            "vibe": "intruiging!",
                        },
                        {
                            "title": "Harry Potter and the Deathly Hallows",
                            "author": "J.K. Rowling",
                            "vibe": "euphoric!",
                        },
                    ],
                    "book_count": 7,
                },
            },
            "structured_output_with_nested_models_scenario:strict:gpt-4": {
                "type": "exception",
                "exception_type": "BadRequestError",
                "exception_message": "Error code: 400 - {'error': {'message': \"Invalid parameter: 'response_format' of type 'json_schema' is not supported with this model. Learn more about supported models at the Structured Outputs guide: https://platform.openai.com/docs/guides/structured-outputs\", 'type': 'invalid_request_error', 'param': None, 'code': None}}",
                "status_code": 400,
            },
            "structured_output_with_nested_models_scenario:tool:gpt-4": {
                "type": "raw_content",
                "content": [
                    ToolCall(
                        id="call_qnyQJGNcZlLmKZehgxyY4oWY",
                        name="__mirascope_formatted_output_tool__.__assistant",
                        args="""\
{
  "series_name": "Harry Potter",
  "author": "J.K. Rowling",
  "books": [
    {
      "title": "Harry Potter and the Philosopher's Stone",
      "author": "J.K. Rowling",
      "vibe": "Fantasy, Adventure"
    },
    {
      "title": "Harry Potter and the Chamber of Secrets",
      "author": "J.K. Rowling",
      "vibe": "Fantasy, Adventure"
    },
    {
      "title": "Harry Potter and the Prisoner of Azkaban",
      "author": "J.K. Rowling",
      "vibe": "Fantasy, Adventure"
    },
    {
      "title": "Harry Potter and the Goblet of Fire",
      "author": "J.K. Rowling",
      "vibe": "Fantasy, Adventure"
    },
    {
      "title": "Harry Potter and the Order of the Phoenix",
      "author": "J.K. Rowling",
      "vibe": "Fantasy, Adventure"
    },
    {
      "title": "Harry Potter and the Half-Blood Prince",
      "author": "J.K. Rowling",
      "vibe": "Fantasy, Adventure"
    },
    {
      "title": "Harry Potter and the Deathly Hallows",
      "author": "J.K. Rowling",
      "vibe": "Fantasy, Adventure"
    }
  ],
  "book_count": 7
}\
""",
                    )
                ],
            },
            "structured_output_with_nested_models_scenario:json:gpt-4": {
                "type": "formatted_output",
                "model_dump": {
                    "series_name": "Harry Potter",
                    "author": "J.K. Rowling",
                    "books": [
                        {
                            "title": "Harry Potter and the Philosopher's Stone",
                            "author": "J.K. Rowling",
                            "vibe": "intruiging!",
                        },
                        {
                            "title": "Harry Potter and the Chamber of Secrets",
                            "author": "J.K. Rowling",
                            "vibe": "mysterious!",
                        },
                        {
                            "title": "Harry Potter and the Prisoner of Azkaban",
                            "author": "J.K. Rowling",
                            "vibe": "euphoric!",
                        },
                        {
                            "title": "Harry Potter and the Goblet of Fire",
                            "author": "J.K. Rowling",
                            "vibe": "soul_searching!",
                        },
                    ],
                    "book_count": 4,
                },
            },
        }
    )

    assert actual == expected[f"{scenario_id}:{format_mode}:{test_model_id}"]
