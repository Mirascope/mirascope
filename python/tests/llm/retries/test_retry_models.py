"""Tests for RetryModel properties."""

from mirascope import llm

from .mock_provider import MockProvider


def test_model_id_property(mock_provider: MockProvider) -> None:  # noqa: ARG001
    """Test that model_id delegates to wrapped model."""
    model = llm.Model("mock/test-model")
    retry_model = llm.retry(model, max_retries=2)

    assert retry_model.model_id == "mock/test-model"


def test_params_property(mock_provider: MockProvider) -> None:  # noqa: ARG001
    """Test that params delegates to wrapped model."""
    model = llm.Model("mock/test-model")
    retry_model = llm.retry(model, max_retries=2)

    assert retry_model.params is not None
