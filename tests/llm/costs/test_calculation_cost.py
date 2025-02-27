"""Integration tests for cost calculation with mock implementations."""

import pytest
from unittest.mock import MagicMock
from mirascope.core.base.types import CostMetadata
from mirascope.llm.costs import calculate_cost


# Import the main function to test


@pytest.fixture
def setup_mock_implementations(monkeypatch):
    """Set up mock implementations for all provider-specific cost calculation functions."""
    # Create mock objects for each provider function
    mock_providers = {
        "_openai_calculate_cost": MagicMock(return_value=0.05),
        "_anthropic_calculate_cost": MagicMock(return_value=0.06),
        "_azure_calculate_cost": MagicMock(return_value=0.04),
        "_bedrock_calculate_cost": MagicMock(return_value=0.07),
        "_cohere_calculate_cost": MagicMock(return_value=0.03),
        "_gemini_calculate_cost": MagicMock(return_value=0.08),
        "_google_calculate_cost": MagicMock(return_value=0.09),
        "_groq_calculate_cost": MagicMock(return_value=0.02),
        "_mistral_calculate_cost": MagicMock(return_value=0.01),
        "_vertex_calculate_cost": MagicMock(return_value=0.10),
        "_xai_calculate_cost": MagicMock(return_value=0.11),
    }

    # Patch each provider-specific function
    for func_name, mock_func in mock_providers.items():
        monkeypatch.setattr(f"cost_utils.{func_name}", mock_func)

    # Return the mock objects for use in tests
    return mock_providers


def test_all_providers_with_mocks(setup_mock_implementations):
    """Test all supported providers with mock implementations."""
    # List of all supported providers
    providers = [
        "openai",
        "anthropic",
        "azure",
        "bedrock",
        "cohere",
        "gemini",
        "google",
        "groq",
        "mistral",
        "vertex",
        "xai",
    ]

    # Expected values (matching the mock return values)
    expected_values = {
        "openai": 0.05,
        "anthropic": 0.06,
        "azure": 0.04,
        "bedrock": 0.07,
        "cohere": 0.03,
        "gemini": 0.08,
        "google": 0.09,
        "groq": 0.02,
        "mistral": 0.01,
        "vertex": 0.10,
        "xai": 0.11,
    }

    # Test metadata
    metadata = CostMetadata(input_tokens=100, output_tokens=50, cached_tokens=10)

    # Test each provider
    for provider in providers:
        result = calculate_cost(
            provider=provider, model="test-model", metadata=metadata
        )
        assert result == expected_values[provider], f"Failed for provider {provider}"

        # Verify the corresponding mock was called with the correct parameters
        provider_func = setup_mock_implementations[f"_{provider}_calculate_cost"]
        provider_func.assert_called_with(metadata, "test-model")


def test_metadata_modification(setup_mock_implementations):
    """Test that the calculate_cost function properly initializes metadata."""
    # Get one of the mock implementations
    mock_openai = setup_mock_implementations["_openai_calculate_cost"]

    # Test with empty metadata
    metadata = CostMetadata()
    calculate_cost(provider="openai", model="test-model", metadata=metadata)

    # Verify that cached_tokens was initialized to 0
    assert metadata.cached_tokens == 0

    # Reset the mock
    mock_openai.reset_mock()

    # Test with None metadata
    calculate_cost(provider="openai", model="test-model", metadata=None)

    # Get the metadata that was passed to the mock
    called_metadata = mock_openai.call_args[0][0]

    # Verify that a new metadata object was created with cached_tokens set to 0
    assert isinstance(called_metadata, CostMetadata)
    assert called_metadata.cached_tokens == 0


def test_custom_mock_behavior(monkeypatch):
    """Test with custom mock behavior for a specific provider."""

    # Create a mock with custom behavior that depends on the model
    def mock_anthropic_calc(metadata, model):
        if model == "claude-3-opus":
            return 0.12
        elif model == "claude-3-sonnet":
            return 0.08
        else:
            return 0.04

    # Patch the anthropic calculate_cost function
    monkeypatch.setattr("cost_utils._anthropic_calculate_cost", mock_anthropic_calc)

    # Test metadata
    metadata = CostMetadata(input_tokens=100, output_tokens=50, cached_tokens=10)

    # Test with different models
    assert calculate_cost("anthropic", "claude-3-opus", metadata) == 0.12
    assert calculate_cost("anthropic", "claude-3-sonnet", metadata) == 0.08
    assert calculate_cost("anthropic", "claude-3-haiku", metadata) == 0.04


def test_mock_error_handling(monkeypatch):
    """Test error handling with mock implementations."""

    # Create a mock that raises an exception
    def mock_openai_error(metadata, model):
        raise ValueError("API error simulation")

    # Patch the openai calculate_cost function
    monkeypatch.setattr("cost_utils._openai_calculate_cost", mock_openai_error)

    # Verify that the exception is propagated
    with pytest.raises(ValueError, match="API error simulation"):
        calculate_cost("openai", "gpt-4", CostMetadata())


def test_litellm_mock_invariant(setup_mock_implementations):
    """Test that LiteLLM always returns None regardless of mocks."""
    # Even with all the mocks set up, litellm should still return None
    metadata = CostMetadata(input_tokens=100, output_tokens=50, cached_tokens=10)

    result = calculate_cost(provider="litellm", model="any-model", metadata=metadata)
    assert result is None

    # Verify that none of the mocks were called
    for mock_func in setup_mock_implementations.values():
        mock_func.assert_not_called()
