import pytest

from mirascope.core.base.types import CostMetadata
from mirascope.core.costs import calculate_cost


def test_calculate_cost_with_none_metadata(monkeypatch):
    """Test that if metadata is None, a new CostMetadata is created with cached_tokens defaulting to 0."""

    def dummy_openai(metadata, model):
        assert isinstance(metadata, CostMetadata)
        assert metadata.cached_tokens == 0
        return 50.0

    monkeypatch.setitem(
        calculate_cost.__globals__, "openai_calculate_cost", dummy_openai
    )

    result = calculate_cost("openai", "gpt-3.5-turbo", None)
    assert result == 50.0


def test_calculate_cost_unknown_provider():
    """Test that an unsupported provider raises a ValueError."""
    metadata = CostMetadata(input_tokens=1, output_tokens=1, cached_tokens=0)
    with pytest.raises(ValueError):
        calculate_cost("unknown_provider", "model", metadata)  # pyright: ignore [reportArgumentType]


@pytest.mark.parametrize(
    "provider,dummy_func_name,expected_cost",
    [
        ("openai", "openai_calculate_cost", 42.0),
        ("anthropic", "anthropic_calculate_cost", 24.0),
        ("azure", "azure_calculate_cost", 12.0),
        ("bedrock", "bedrock_calculate_cost", 8.0),
        ("cohere", "cohere_calculate_cost", 15.0),
        ("gemini", "gemini_calculate_cost", 18.0),
        ("google", "google_calculate_cost", 20.0),
        ("groq", "groq_calculate_cost", 22.0),
        ("mistral", "mistral_calculate_cost", 25.0),
        ("vertex", "vertex_calculate_cost", 30.0),
        ("xai", "xai_calculate_cost", 35.0),
        ("litellm", "litellm_calculate_cost", 35.0),
    ],
)
def test_calculate_cost_providers(
    monkeypatch, provider, dummy_func_name, expected_cost
):
    """Test that calculate_cost correctly routes to the provider-specific cost function."""

    def dummy_func(metadata, model):
        return expected_cost

    monkeypatch.setitem(calculate_cost.__globals__, dummy_func_name, dummy_func)

    metadata = CostMetadata(input_tokens=5, output_tokens=5, cached_tokens=0)
    result = calculate_cost(provider, "dummy_model", metadata)
    assert result == expected_cost
