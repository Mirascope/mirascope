"""Tests for AnthropicClient using shared scenarios."""

import pytest

from mirascope import llm
from tests.llm.clients.scenarios import (
    CLIENT_SCENARIO_IDS,
    FORMATTING_MODES,
    STRUCTURED_SCENARIO_IDS,
    get_scenario,
    get_structured_scenario,
    simple_message_scenario,
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
@pytest.mark.asyncio
async def test_call_async(
    anthropic_client: llm.AnthropicClient,
    scenario_id: str,
) -> None:
    scenario = get_scenario(scenario_id, model_id=TEST_MODEL_ID)
    response = await anthropic_client.call_async(**scenario.call_async_args)
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


@pytest.mark.parametrize("scenario_id", CLIENT_SCENARIO_IDS)
@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_stream_async(
    anthropic_client: llm.AnthropicClient,
    scenario_id: str,
) -> None:
    scenario = get_scenario(scenario_id, model_id=TEST_MODEL_ID)
    response = await anthropic_client.stream_async(**scenario.call_async_args)
    async for _ in response.chunk_stream():
        pass
    scenario.check_response(response)


# TODO: context_call will be tested on all scenarios when we switch to decorator-level
# integration testing.
@pytest.mark.vcr()
def test_context_call(anthropic_client: llm.AnthropicClient) -> None:
    scenario = simple_message_scenario(TEST_MODEL_ID)
    ctx = llm.Context(deps=42)

    response = anthropic_client.context_call(ctx=ctx, **scenario.call_args)
    scenario.check_response(response)


@pytest.mark.vcr()
def test_context_stream(anthropic_client: llm.AnthropicClient) -> None:
    scenario = simple_message_scenario(TEST_MODEL_ID)
    ctx = llm.Context(deps=42)

    stream_response = anthropic_client.context_stream(ctx=ctx, **scenario.call_args)
    for _ in stream_response.chunk_stream():
        pass
    scenario.check_response(stream_response)


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_context_call_async(anthropic_client: llm.AnthropicClient) -> None:
    scenario = simple_message_scenario(TEST_MODEL_ID)
    ctx = llm.Context(deps=42)

    async_response = await anthropic_client.context_call_async(
        ctx=ctx, **scenario.call_async_args
    )
    scenario.check_response(async_response)


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_context_stream_async(anthropic_client: llm.AnthropicClient) -> None:
    scenario = simple_message_scenario(TEST_MODEL_ID)
    ctx = llm.Context(deps=42)

    async_stream_response = await anthropic_client.context_stream_async(
        ctx=ctx, **scenario.call_async_args
    )
    async for _ in async_stream_response.chunk_stream():
        pass
    scenario.check_response(async_stream_response)


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
    except ValueError:
        # Anthropic has no strict mode, so the model outputs regular text with no guidance
        # on formatting.
        # TODO: Have it raise FeatureNotImplementedError or similar
        assert formatting_mode == "strict"
