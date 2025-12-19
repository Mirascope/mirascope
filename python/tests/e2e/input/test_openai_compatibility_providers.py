"""End-to-end tests for OpenAI-compatible providers (together, ollama, etc.)."""

import os

import pytest

from mirascope import llm
from tests.utils import (
    Snapshot,
    snapshot_test,
)

TOGETHER_MODEL_IDS = [
    "meta-llama/Llama-3.3-70B-Instruct-Turbo",
]


@pytest.mark.parametrize("model_id", TOGETHER_MODEL_IDS)
@pytest.mark.vcr
def test_together_provider(model_id: llm.ModelId, snapshot: Snapshot) -> None:
    """Test that Together provider works correctly."""

    @llm.call(model_id)
    def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    llm.register_provider(
        "together", "meta-llama/", api_key=os.getenv("TOGETHER_API_KEY", "test")
    )

    with snapshot_test(snapshot) as snap:
        response = add_numbers(4200, 42)
        assert response.provider_id == "together"
        assert response.provider_model_name == "meta-llama/Llama-3.3-70B-Instruct-Turbo"
        snap.set_response(response)
        assert "4242" in response.pretty(), (
            f"Expected '4242' in response: {response.pretty()}"
        )


def test_together_provider_missing_api_key() -> None:
    """Test that Together provider raises clear error when API key is missing."""
    from mirascope.llm.providers.together import TogetherProvider

    original_key = os.environ.pop("TOGETHER_API_KEY", None)
    try:
        with pytest.raises(ValueError) as exc_info:
            TogetherProvider()
        assert "Together API key is required" in str(exc_info.value)
        assert "TOGETHER_API_KEY" in str(exc_info.value)
    finally:
        if original_key is not None:
            os.environ["TOGETHER_API_KEY"] = original_key


OLLAMA_MODEL_IDS = [
    "ollama/gemma3:4b",
]


@pytest.mark.parametrize("model_id", OLLAMA_MODEL_IDS)
@pytest.mark.vcr
def test_ollama_provider(model_id: llm.ModelId, snapshot: Snapshot) -> None:
    """Test that Ollama provider works correctly."""
    # Clear OLLAMA_BASE_URL to ensure consistent cassette matching
    original_base_url = os.environ.pop("OLLAMA_BASE_URL", None)
    try:

        @llm.call(model_id)
        def add_numbers(a: int, b: int) -> str:
            return f"What is {a} + {b}?"

        llm.register_provider("ollama")

        with snapshot_test(snapshot) as snap:
            response = add_numbers(4200, 42)
            assert response.provider_id == "ollama"
            assert response.provider_model_name == "gemma3:4b"
            snap.set_response(response)
            assert "4242" in response.pretty(), (
                f"Expected '4242' in response: {response.pretty()}"
            )
    finally:
        if original_base_url is not None:
            os.environ["OLLAMA_BASE_URL"] = original_base_url
