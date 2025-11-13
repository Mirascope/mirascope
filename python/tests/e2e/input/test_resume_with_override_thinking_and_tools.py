"""End-to-end tests for resuming with override while using thinking and tools."""

from typing import TypedDict

import pytest

from mirascope import llm
from tests.e2e.conftest import PROVIDER_MODEL_ID_PAIRS
from tests.utils import Snapshot, snapshot_test


class ProviderAndModelId(TypedDict, total=True):
    provider: llm.Provider
    model_id: llm.ModelId


def default_provider_and_model(
    provider: llm.Provider,
) -> ProviderAndModelId:
    """Default provider and model that are distinct from the provider being tested.

    Used to ensure that we can test having the provider under test resume
    from a response that was created by a different provider.
    """
    if provider == "google":
        return {"provider": "anthropic", "model_id": "claude-sonnet-4-0"}
    else:
        return {"provider": "google", "model_id": "gemini-2.5-flash"}


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_resume_with_override_thinking_and_tools(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test call with thinking and tools, resuming with a different model."""

    @llm.tool
    def compute_fib(n: int) -> str:
        """Compute the nth Fibonacci number (1-indexed)."""
        if n == 100:
            return "218922995834555169026"
        return "Not implemented for other values"

    @llm.call(
        **default_provider_and_model(provider),
        thinking=True,
        tools=[compute_fib],
    )
    def fib_query() -> str:
        return "What is the 100th fibonacci number?"

    with snapshot_test(snapshot) as snap:
        primer_response = fib_query()
        assert len(primer_response.tool_calls) >= 1, (
            f"Expected at least one tool call in first response: {primer_response.pretty()}"
        )

        tool_outputs = primer_response.execute_tools()
        with llm.model(provider=provider, model_id=model_id, thinking=False):
            response = primer_response.resume(tool_outputs)

        snap.set_response(response)
