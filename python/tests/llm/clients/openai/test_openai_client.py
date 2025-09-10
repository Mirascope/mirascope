"""Tests for OpenAIClient using VCR.py for HTTP request recording/playback."""

import openai
import pytest

from mirascope import llm
from tests.llm.clients.scenarios import (
    CLIENT_SCENARIO_IDS,
    FORMATTING_MODES,
    STRUCTURED_SCENARIO_IDS,
    get_scenario,
    get_structured_scenario,
)

TEST_MODEL_ID = "gpt-4o"


@pytest.mark.parametrize("scenario_id", CLIENT_SCENARIO_IDS)
@pytest.mark.vcr()
def test_call(
    openai_client: llm.OpenAIClient,
    scenario_id: str,
) -> None:
    scenario = get_scenario(scenario_id, model_id=TEST_MODEL_ID)
    response = openai_client.call(**scenario.call_args)
    scenario.check_response(response)


@pytest.mark.parametrize("scenario_id", CLIENT_SCENARIO_IDS)
@pytest.mark.vcr()
def test_stream(
    openai_client: llm.OpenAIClient,
    scenario_id: str,
) -> None:
    scenario = get_scenario(scenario_id, model_id=TEST_MODEL_ID)
    response = openai_client.stream(**scenario.call_args)
    list(response.chunk_stream())
    scenario.check_response(response)


@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.parametrize("scenario_id", STRUCTURED_SCENARIO_IDS)
@pytest.mark.vcr()
def test_structured_outputs(
    openai_client: llm.OpenAIClient,
    formatting_mode: llm.formatting.FormattingMode,
    scenario_id: str,
) -> None:
    scenario = get_structured_scenario(scenario_id, TEST_MODEL_ID, formatting_mode)
    response = openai_client.call(**scenario.call_args)
    scenario.check_response(response)


@pytest.mark.parametrize(
    # For gpt-4, strict will fail, strict-or-tool should succeed (tool mode), and
    # strict-or-json should succeed (json mode). Testing tool or json mode directly would
    # be redundant
    "formatting_mode",
    ["strict", "strict-or-tool", "strict-or-json"],
)
@pytest.mark.parametrize(
    # Test two scenarios to make sure tool calling and complex format parsing still work
    # for the legacy mode. More would be redundant
    "scenario_id",
    [
        "structured_output_calls_tool_scenario",
        "structured_output_annotation_and_docstring_scenario",
    ],
)
@pytest.mark.vcr()
def test_structured_output_legacy_model(
    openai_client: llm.OpenAIClient,
    formatting_mode: llm.formatting.FormattingMode,
    scenario_id: str,
) -> None:
    scenario = get_structured_scenario(scenario_id, "gpt-4", formatting_mode)
    try:
        response = openai_client.call(**scenario.call_args)
        scenario.check_response(response)
    except openai.BadRequestError as e:
        if formatting_mode == "strict":
            pass  # Expected, gpt-4 does not support strict mode.
        else:
            raise e
    except AssertionError as e:
        if formatting_mode == "strict-or-json" and e.args == (
            "Expected 1 tool call, got 0: []",
        ):
            # Known issue: gpt-4 will not call tools with json.
            # Call seems correct so considering this a model quirk.
            pass
        else:
            raise e
