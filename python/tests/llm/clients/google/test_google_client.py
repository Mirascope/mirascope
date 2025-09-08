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
from tests.llm.clients.conftest import CLIENT_SCENARIO_IDS, STRUCTURED_SCENARIO_IDS


@pytest.mark.parametrize("scenario_id", CLIENT_SCENARIO_IDS)
@pytest.mark.vcr()
def test_call(
    google_client: llm.GoogleClient,
    scenario_id: str,
    request: pytest.FixtureRequest,
) -> None:
    """Test call method with all scenarios."""
    # Skip structured scenarios as Google doesn't have structured output support yet
    if scenario_id in STRUCTURED_SCENARIO_IDS:
        pytest.skip(f"Structured scenario {scenario_id} not supported by Google yet")

    kwargs = request.getfixturevalue(scenario_id)
    response = google_client.call(model_id="gemini-2.0-flash", **kwargs)
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
    # Skip structured scenarios as Google doesn't have structured output support yet
    if scenario_id in STRUCTURED_SCENARIO_IDS:
        pytest.skip(f"Structured scenario {scenario_id} not supported by Google yet")

    kwargs = request.getfixturevalue(scenario_id)
    stream_response = google_client.stream(model_id="gemini-2.0-flash", **kwargs)
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
        }
    )
    assert utils.stream_response_snapshot_dict(stream_response) == expected[scenario_id]


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
        model_id="gemini-2.0-flash",
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
