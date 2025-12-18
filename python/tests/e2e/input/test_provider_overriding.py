"""End-to-end tests for a LLM call without tools or structured outputs."""

import os

import pytest

from mirascope import llm
from tests.utils import (
    Snapshot,
    snapshot_test,
)


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


OPENAI_MODEL_IDS = [
    "openai/gpt-4o-mini",
    "openai/gpt-4o-mini:completions",
    "openai/gpt-4o-mini:responses",
]


@pytest.mark.parametrize("model_id", OPENAI_MODEL_IDS)
@pytest.mark.vcr
def test_openai_completions_provider(model_id: llm.ModelId, snapshot: Snapshot) -> None:
    """Test that registering openai:completions enforces completions API usage."""

    @llm.call(model_id)
    def simple_call() -> str:
        return "Say hello"

    llm.register_provider("openai:completions")

    with snapshot_test(snapshot) as snap:
        response = simple_call()
        assert response.provider_id == "openai:completions"
        assert response.provider_model_name.endswith(":completions")
        snap.set_response(response)


@pytest.mark.parametrize("model_id", OPENAI_MODEL_IDS)
@pytest.mark.vcr
def test_openai_responses_provider(model_id: llm.ModelId, snapshot: Snapshot) -> None:
    """Test that registering openai:responses enforces responses API usage."""

    @llm.call(model_id)
    def simple_call() -> str:
        return "Say hello"

    llm.register_provider("openai:responses")

    with snapshot_test(snapshot) as snap:
        response = simple_call()
        assert response.provider_id == "openai:responses"
        assert response.provider_model_name.endswith(":responses")
        snap.set_response(response)
