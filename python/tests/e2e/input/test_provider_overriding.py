"""End-to-end tests for a LLM call without tools or structured outputs."""

import os
from collections.abc import Generator

import pytest

from mirascope import llm
from mirascope.llm.providers.provider_registry import (
    PROVIDER_REGISTRY,
)
from tests.utils import (
    Snapshot,
    snapshot_test,
)


@pytest.fixture(autouse=True)
def reset_provider_registry() -> Generator[None, None, None]:
    """Reset the provider registry before and after each test."""
    PROVIDER_REGISTRY.clear()
    yield
    PROVIDER_REGISTRY.clear()


@pytest.mark.parametrize("model_id", ["anthropic/claude-sonnet-4-5"])
@pytest.mark.vcr
def test_call_non_openai_models_through_openai(
    model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test calling non-OpenAI models using the openai client via provider overriding."""

    @llm.call(model_id)
    def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    llm.register_provider(
        "openai",
        "anthropic/",
        base_url="https://api.anthropic.com/v1/",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
    )
    with snapshot_test(snapshot) as snap:
        response = add_numbers(4200, 42)
        assert response.provider_id == "openai"
        snap.set_response(response)
        assert "4242" in response.pretty(), (
            f"Expected '4242' in response: {response.pretty()}"
        )
