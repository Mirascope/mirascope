"""End-to-end tests for prompt caching."""

import pytest

from mirascope import llm
from tests.e2e.conftest import E2E_MODEL_IDS
from tests.utils import Snapshot, snapshot_test


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
def test_web_search_tool(
    model_id: llm.ModelId,
    snapshot: Snapshot,
) -> None:
    """Test handling of the provider's web search tool."""

    @llm.call(model_id, tools=[llm.WebSearchTool()])
    def crypto_price_lookup() -> str:
        # Assert the date since the models will otherwise complain that they can't predict the future
        return "Jan 1, 2026 is a date in the past. Use the web search tool to lookup the price of bitcoin on that date."

    with snapshot_test(snapshot) as snap:
        response = crypto_price_lookup()
        # Resume just to make sure we handle re-encoding correctly, etc.
        response = response.resume(
            "Please also look up the price of Ethereum on that date"
        )
        snap.set_response(response)


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
def test_web_search_tool_stream(
    model_id: llm.ModelId,
    snapshot: Snapshot,
) -> None:
    """Test streaming handling of the provider's web search tool."""

    @llm.call(model_id, tools=[llm.WebSearchTool()])
    def crypto_price_lookup() -> str:
        # Assert the date since the models will otherwise complain that they can't predict the future
        return "Jan 1, 2026 is a date in the past. Use the web search tool to lookup the price of bitcoin on that date."

    with snapshot_test(snapshot) as snap:
        response = crypto_price_lookup.stream()
        response.finish()
        # Resume just to make sure we handle re-encoding correctly, etc.
        response = response.resume(
            "Please also look up the price of Ethereum on that date"
        )
        response.finish()
        snap.set_response(response)
