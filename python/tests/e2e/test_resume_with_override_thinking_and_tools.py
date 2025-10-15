"""End-to-end tests for resuming with override while using thinking and tools."""

from typing import TypedDict

import pytest

from mirascope import llm
from tests.e2e.conftest import PROVIDER_MODEL_ID_PAIRS, Snapshot
from tests.utils import response_snapshot_dict, stream_response_snapshot_dict


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
    if provider == "anthropic":
        return {"provider": "google", "model_id": "gemini-2.5-flash"}
    else:
        return {"provider": "anthropic", "model_id": "claude-sonnet-4-0"}


# ============= SYNC TESTS =============


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_resume_with_override_thinking_and_tools_sync(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test synchronous call with thinking and tools, resuming with a different model."""

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

    primer_response = fib_query()
    assert len(primer_response.tool_calls) >= 1, (
        f"Expected at least one tool call in first response: {primer_response.pretty()}"
    )

    tool_outputs = primer_response.execute_tools()
    with llm.model(provider=provider, model_id=model_id, thinking=False):
        response = primer_response.resume(tool_outputs)

    assert response_snapshot_dict(response) == snapshot


# ============= ASYNC TESTS =============


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_resume_with_override_thinking_and_tools_async(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test asynchronous call with thinking and tools, resuming with a different model."""

    @llm.tool
    async def compute_fib(n: int) -> str:
        """Compute the nth Fibonacci number (1-indexed)."""
        if n == 100:
            return "218922995834555169026"
        return "Not implemented for other values"

    @llm.call(
        **default_provider_and_model(provider),
        thinking=True,
        tools=[compute_fib],
    )
    async def fib_query() -> str:
        return "What is the 100th fibonacci number?"

    primer_response = await fib_query()
    assert len(primer_response.tool_calls) >= 1, (
        f"Expected at least one tool call in first response: {primer_response.pretty()}"
    )

    tool_outputs = await primer_response.execute_tools()
    with llm.model(provider=provider, model_id=model_id, thinking=False):
        response = await primer_response.resume(tool_outputs)

    assert response_snapshot_dict(response) == snapshot


# ============= STREAM TESTS =============


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_resume_with_override_thinking_and_tools_stream(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test streaming call with thinking and tools, resuming with a different model."""

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

    primer_response = fib_query.stream()
    primer_response.finish()
    assert len(primer_response.tool_calls) >= 1, (
        f"Expected at least one tool call in first response: {primer_response.pretty()}"
    )

    tool_outputs = primer_response.execute_tools()
    with llm.model(provider=provider, model_id=model_id, thinking=False):
        response = primer_response.resume(tool_outputs)
    response.finish()

    assert stream_response_snapshot_dict(response) == snapshot


# ============= ASYNC STREAM TESTS =============


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_resume_with_override_thinking_and_tools_async_stream(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test async streaming call with thinking and tools, resuming with a different model."""

    @llm.tool
    async def compute_fib(n: int) -> str:
        """Compute the nth Fibonacci number (1-indexed)."""
        if n == 100:
            return "218922995834555169026"
        return "Not implemented for other values"

    @llm.call(
        **default_provider_and_model(provider),
        thinking=True,
        tools=[compute_fib],
    )
    async def fib_query() -> str:
        return "What is the 100th fibonacci number?"

    primer_response = await fib_query.stream()
    await primer_response.finish()
    assert len(primer_response.tool_calls) >= 1, (
        f"Expected at least one tool call in first response: {primer_response.pretty()}"
    )

    tool_outputs = await primer_response.execute_tools()
    with llm.model(provider=provider, model_id=model_id, thinking=False):
        response = await primer_response.resume(tool_outputs)
    await response.finish()

    assert stream_response_snapshot_dict(response) == snapshot
