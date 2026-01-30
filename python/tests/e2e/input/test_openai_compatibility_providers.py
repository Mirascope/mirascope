"""End-to-end tests for OpenAI-compatible providers (together, ollama, openrouter)."""

import os
from collections.abc import Generator

import pytest

from mirascope import llm
from tests.utils import (
    Snapshot,
    snapshot_test,
)

# --- OpenRouter tests ---

OPENROUTER_OPENAI_MODEL: llm.ModelId = "openrouter/openai/gpt-4o"
OPENROUTER_REASONING_MODEL: llm.ModelId = "openrouter/openai/o1"
OPENROUTER_ANTHROPIC_MODEL: llm.ModelId = (
    "openrouter/anthropic/claude-3-5-sonnet-20241022"
)


@pytest.fixture
def register_openrouter(reset_provider_registry: None) -> Generator[None, None, None]:
    """Register OpenRouter provider for tests.

    Depends on reset_provider_registry to ensure clean state.
    """
    _ = reset_provider_registry  # Ensure dependency is resolved
    llm.register_provider("openrouter", scope="openrouter/")
    yield


@pytest.mark.parametrize(
    "model_id", [OPENROUTER_OPENAI_MODEL, OPENROUTER_ANTHROPIC_MODEL]
)
@pytest.mark.vcr
def test_openrouter_sync(
    model_id: llm.ModelId,
    register_openrouter: None,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test OpenRouter sync call with different model types."""

    @llm.call(model_id)
    def simple_call() -> str:
        return "Say hello in one word"

    with snapshot_test(snapshot, caplog) as snap:
        response = simple_call()
        snap.set_response(response)


@pytest.mark.parametrize(
    "model_id", [OPENROUTER_OPENAI_MODEL, OPENROUTER_ANTHROPIC_MODEL]
)
@pytest.mark.vcr
def test_openrouter_stream(
    model_id: llm.ModelId,
    register_openrouter: None,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test OpenRouter streaming with different model types."""

    @llm.call(model_id)
    def simple_call() -> str:
        return "Say hello in one word"

    with snapshot_test(snapshot, caplog) as snap:
        stream = simple_call.stream()
        stream.finish()
        snap.set_response(stream)


@pytest.mark.parametrize(
    "model_id", [OPENROUTER_OPENAI_MODEL, OPENROUTER_ANTHROPIC_MODEL]
)
@pytest.mark.vcr
def test_openrouter_with_temperature(
    model_id: llm.ModelId,
    register_openrouter: None,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that temperature param is accepted for non-reasoning models.

    Both openai/gpt-4o (non-reasoning OpenAI model) and anthropic/claude-3-5-sonnet
    (via empty CompletionsModelFeatureInfo) should accept temperature without warnings.
    """

    @llm.call(model_id, temperature=0.5)
    def simple_call() -> str:
        return "Say hello"

    with snapshot_test(snapshot, caplog) as snap:
        response = simple_call()
        snap.set_response(response)

    # Verify no "Skipping unsupported parameter" warning was logged
    assert "Skipping unsupported parameter: temperature" not in caplog.text


@pytest.mark.parametrize("model_id", [OPENROUTER_REASONING_MODEL])
@pytest.mark.vcr
def test_openrouter_reasoning_model_skips_temperature(
    model_id: llm.ModelId,
    register_openrouter: None,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that reasoning models via OpenRouter skip temperature with warning.

    o1 is not in NON_REASONING_MODELS, so it's treated as a reasoning model.
    Temperature should be skipped with a warning logged.
    """

    @llm.call(model_id, temperature=0.5)
    def simple_call() -> str:
        return "What is 2+2?"

    with snapshot_test(snapshot, caplog) as snap:
        response = simple_call()
        snap.set_response(response)

    # Verify warning was logged about skipping temperature
    assert "Skipping unsupported parameter: temperature" in caplog.text


# --- Together tests ---

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
