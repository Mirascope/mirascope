"""Tests for AnthropicClient using shared scenarios."""

import json

import pytest

from mirascope import llm
from tests.llm.clients.scenarios import (
    CLIENT_SCENARIO_IDS,
    FORMATTING_MODES,
    STRUCTURED_SCENARIO_IDS,
    get_scenario,
    get_structured_scenario,
)

TEST_MODEL_ID = "claude-sonnet-4-0"


@pytest.mark.parametrize("scenario_id", CLIENT_SCENARIO_IDS)
@pytest.mark.vcr()
def test_call(
    anthropic_client: llm.AnthropicClient,
    scenario_id: str,
) -> None:
    """Test call method with all scenarios."""

    scenario = get_scenario(scenario_id, model_id=TEST_MODEL_ID)
    response = anthropic_client.call(**scenario.call_args)
    scenario.check_response(response)


@pytest.mark.parametrize("scenario_id", CLIENT_SCENARIO_IDS)
@pytest.mark.vcr()
def test_stream(
    anthropic_client: llm.AnthropicClient,
    scenario_id: str,
) -> None:
    """Test stream method with all scenarios."""

    scenario = get_scenario(scenario_id, model_id=TEST_MODEL_ID)
    response = anthropic_client.stream(**scenario.call_args)
    list(response.chunk_stream())
    scenario.check_response(response)


@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.parametrize("scenario_id", STRUCTURED_SCENARIO_IDS)
@pytest.mark.vcr()
def test_structured_outputs(
    anthropic_client: llm.AnthropicClient,
    formatting_mode: llm.formatting.FormattingMode,
    scenario_id: str,
) -> None:
    scenario = get_structured_scenario(scenario_id, TEST_MODEL_ID, formatting_mode)
    try:
        response = anthropic_client.call(**scenario.call_args)
        scenario.check_response(response)
    except json.decoder.JSONDecodeError as e:
        if formatting_mode == "strict":
            # Expected; anthropic has no strict mode, so the call to .format() will fail
            pass
        else:
            raise e
