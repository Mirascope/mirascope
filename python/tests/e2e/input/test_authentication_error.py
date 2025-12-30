"""End-to-end tests for AuthenticationError when using invalid API keys."""

from __future__ import annotations

from collections.abc import Generator

import pytest

from mirascope import llm
from tests.e2e.conftest import E2E_MODEL_IDS

# Filter out MLX models since they don't require API keys
API_PROVIDER_MODEL_IDS = [
    model_id for model_id in E2E_MODEL_IDS if not model_id.startswith("mlx-community/")
]


@pytest.fixture(autouse=True)
def register_providers_with_invalid_keys() -> Generator[None, None, None]:
    """Register providers with invalid API keys for authentication error tests."""
    # Register providers with obviously invalid API keys
    anthropic_provider = llm.register_provider("anthropic", api_key="invalid-key-12345")
    llm.register_provider("openai", api_key="invalid-key-12345")
    llm.register_provider("google", api_key="invalid-key-12345")

    assert isinstance(anthropic_provider, llm.providers.AnthropicProvider)
    beta_provider = anthropic_provider._beta_provider  # pyright: ignore[reportPrivateUsage]
    assert beta_provider.client.api_key == "invalid-key-12345"
    llm.register_provider(beta_provider, "anthropic-beta/")

    yield


@pytest.mark.parametrize("model_id", API_PROVIDER_MODEL_IDS)
@pytest.mark.vcr
def test_authentication_error(model_id: llm.ModelId) -> None:
    """Test that calling with invalid API key raises AuthenticationError."""

    @llm.call(model_id)
    def test_call() -> str:
        return "This should fail with AuthenticationError"

    with pytest.raises(llm.AuthenticationError):
        test_call()


@pytest.mark.parametrize("model_id", API_PROVIDER_MODEL_IDS)
@pytest.mark.vcr
def test_authentication_error_stream(model_id: llm.ModelId) -> None:
    """Test that streaming with invalid API key raises AuthenticationError."""

    @llm.call(model_id)
    def test_stream() -> str:
        return "This should fail with AuthenticationError"

    with pytest.raises(llm.AuthenticationError):
        stream = test_stream.stream()
        stream.finish()
