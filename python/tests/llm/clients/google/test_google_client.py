"""Tests for GoogleClient using VCR.py for HTTP request recording/playback."""

from unittest.mock import MagicMock, patch

import pytest
from google.genai.errors import ClientError as GoogleClientError
from inline_snapshot import snapshot

from mirascope import llm
from tests import utils
from tests.llm.clients.scenarios import (
    CLIENT_SCENARIO_IDS,
    FORMATTING_MODES,
    STRUCTURED_SCENARIO_IDS,
    get_scenario,
    get_structured_scenario,
)

TEST_MODEL_ID = "gemini-2.5-flash"


@pytest.mark.parametrize("scenario_id", CLIENT_SCENARIO_IDS)
@pytest.mark.vcr()
def test_call(
    google_client: llm.GoogleClient,
    scenario_id: str,
) -> None:
    """Test call method with all scenarios."""

    scenario = get_scenario(scenario_id, model_id=TEST_MODEL_ID)
    response = google_client.call(**scenario.call_args)
    scenario.check_response(response)


@pytest.mark.parametrize("scenario_id", CLIENT_SCENARIO_IDS)
@pytest.mark.vcr()
def test_stream(
    google_client: llm.GoogleClient,
    scenario_id: str,
    request: pytest.FixtureRequest,
) -> None:
    """Test stream method with all scenarios."""

    scenario = get_scenario(scenario_id, model_id=TEST_MODEL_ID)
    response = google_client.stream(**scenario.call_args)
    list(response.chunk_stream())
    scenario.check_response(response)


@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.parametrize("scenario_id", STRUCTURED_SCENARIO_IDS)
@pytest.mark.vcr()
def test_structured_outputs(
    google_client: llm.GoogleClient,
    formatting_mode: llm.formatting.FormattingMode,
    scenario_id: str,
) -> None:
    scenario = get_structured_scenario(scenario_id, TEST_MODEL_ID, formatting_mode)
    try:
        response = google_client.call(**scenario.call_args)
        scenario.check_response(response)
    except GoogleClientError:
        if (
            scenario_id == "structured_output_calls_tools_scenario"
            and formatting_mode in ["strict", "strict-or-json", "json"]
        ):
            pass  # Known issue, Google doesn't allow tool calling in strict or json mode.


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


# Line coverage for a Google-specific edge case
@pytest.mark.vcr()
def test_call_no_output(google_client: llm.GoogleClient) -> None:
    """Test call where assistant generates nothing."""
    messages = [
        llm.messages.system("Do not emit ANY output, terminate immediately."),
        llm.messages.user(""),
    ]

    response = google_client.call(
        model_id="gemini-2.0-flash",  # Note: Does not proc with gemini-2.5-flash
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
