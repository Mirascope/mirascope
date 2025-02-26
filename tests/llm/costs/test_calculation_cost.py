"""Tests for the unified cost calculation function."""

from unittest.mock import patch

import pytest

from mirascope.core.base.types import CostMetadata
from mirascope.llm.costs.calculate_cost import calculate_cost


# Test for each provider implementation
@pytest.mark.parametrize(
    "provider,mock_path,mock_function_name",
    [
        ("openai", "mirascope.llm.costs._openai_calculate_cost", "calculate_cost"),
        (
            "anthropic",
            "mirascope.llm.costs._anthropic_calculate_cost",
            "calculate_cost",
        ),
        ("azure", "mirascope.llm.costs._azure_calculate_cost", "calculate_cost"),
        ("bedrock", "mirascope.llm.costs._bedrock_calculate_cost", "calculate_cost"),
        ("cohere", "mirascope.llm.costs._cohere_calculate_cost", "calculate_cost"),
        ("gemini", "mirascope.llm.costs._gemini_calculate_cost", "calculate_cost"),
        ("google", "mirascope.llm.costs._google_calculate_cost", "calculate_cost"),
        ("groq", "mirascope.llm.costs._groq_calculate_cost", "calculate_cost"),
        ("mistral", "mirascope.llm.costs._mistral_calculate_cost", "calculate_cost"),
        ("xai", "mirascope.llm.costs._xai_calculate_cost", "calculate_cost"),
    ],
)
def test_calculate_cost_routes_to_provider(provider, mock_path, mock_function_name):
    """Test that calculate_cost correctly routes to provider-specific implementation."""
    input_tokens = 1000
    output_tokens = 500
    cached_tokens = 200
    model = "test-model"
    expected_cost = 0.123

    with patch(f"{mock_path}.{mock_function_name}") as mock_provider_calculate_cost:
        mock_provider_calculate_cost.return_value = expected_cost

        result = calculate_cost(
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
        )

        mock_provider_calculate_cost.assert_called_once_with(
            input_tokens, cached_tokens, output_tokens, model
        )
        assert result == expected_cost


def test_calculate_cost_vertex_with_context_length():
    """Test that vertex calculate_cost receives context_length parameter."""
    input_tokens = 1000
    output_tokens = 500
    cached_tokens = 200
    model = "test-model"
    expected_cost = 0.456
    context_length = 8192
    metadata = CostMetadata(context_length=context_length)

    with patch(
        "mirascope.llm.costs._vertex_calculate_cost.calculate_cost"
    ) as mock_vertex:
        mock_vertex.return_value = expected_cost

        result = calculate_cost(
            provider="vertex",
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
            metadata=metadata,
        )

        mock_vertex.assert_called_once_with(
            input_tokens,
            cached_tokens,
            output_tokens,
            model,
            context_length=context_length,
        )
        assert result == expected_cost


def test_calculate_cost_default_values():
    """Test that calculate_cost handles default values correctly."""
    input_tokens = 1000
    output_tokens = 500
    model = "test-model"
    expected_cost = 0.789

    # Act & Assert - Test with cached_tokens=None
    with patch(
        "mirascope.llm.costs._openai_calculate_cost.calculate_cost"
    ) as mock_openai:
        mock_openai.return_value = expected_cost

        result = calculate_cost(
            provider="openai",
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=None,
        )

        mock_openai.assert_called_once_with(input_tokens, 0, output_tokens, model)
        assert result == expected_cost


# Test metadata default handling
def test_calculate_cost_default_metadata():
    """Test that calculate_cost creates empty metadata when None provided."""
    input_tokens = 1000
    output_tokens = 500
    cached_tokens = 200
    model = "test-model"
    expected_cost = 0.321

    with patch(
        "mirascope.llm.costs._openai_calculate_cost.calculate_cost"
    ) as mock_openai:
        mock_openai.return_value = expected_cost

        result = calculate_cost(
            provider="openai",
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
            metadata=None,  # Testing default handling
        )

        mock_openai.assert_called_once_with(
            input_tokens, cached_tokens, output_tokens, model
        )
        assert result == expected_cost


def test_calculate_cost_litellm():
    """Test that calculate_cost returns None for LiteLLM provider."""
    result = calculate_cost(
        provider="litellm",
        model="some-model",
        input_tokens=1000,
        output_tokens=500,
    )

    assert result is None


def test_calculate_cost_unsupported_provider():
    """Test that calculate_cost raises ValueError for unsupported providers."""
    with pytest.raises(ValueError) as excinfo:
        calculate_cost(
            provider="unknown_provider",  # type: ignore
            model="some-model",
            input_tokens=1000,
            output_tokens=500,
        )

    assert "Unsupported provider" in str(excinfo.value)
