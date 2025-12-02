"""Tests for the Model class."""

from unittest.mock import MagicMock

import pytest

from mirascope import llm


def test_client_pulled_from_context_at_call_time() -> None:
    """Test that models get client at call time, not construction time."""
    model = llm.use_model("openai/gpt-4o")

    custom_client = llm.client("openai", api_key="test-key")

    mock_call = MagicMock(return_value=MagicMock())
    custom_client.call = mock_call

    with custom_client:
        model.call(messages=[llm.messages.user("Hello")])

    mock_call.assert_called_once()


def test_use_model_without_context() -> None:
    """Test that use_model creates a new Model when no context is set."""
    model = llm.use_model("openai/gpt-4o")

    assert model.provider == "openai"
    assert model.model_id == "openai/gpt-4o"


def test_use_model_with_context() -> None:
    """Test that use_model returns the context model when one is set."""
    with llm.model("anthropic/claude-sonnet-4-0"):
        model = llm.use_model("openai/gpt-4o")

        assert model.provider == "anthropic"
        assert model.model_id == "anthropic/claude-sonnet-4-0"


def test_direct_model_instantiation_ignores_context() -> None:
    """Test that direct Model instantiation ignores context (hardcoding behavior)."""
    with llm.model("openai/claude-sonnet-4-0"):
        model = llm.Model("openai/gpt-4o")

        assert model.provider == "openai"
        assert model.model_id == "openai/gpt-4o"


def test_value_error_invalid_models() -> None:
    """Test that invalid model_ids raise appropriate ValueErrors."""
    with pytest.raises(ValueError, match="Unknown provider: 'nonexistent'"):
        llm.call("nonexistent/gpt-5-mini")

    with pytest.raises(ValueError, match="Invalid model_id format"):
        llm.call("really-cool-model-i-heard-about")


def test_use_model_accepts_model_instance() -> None:
    """Test that use_model accepts a Model instance."""
    model_instance = llm.Model("anthropic/claude-sonnet-4-0", temperature=0.7)
    model = llm.use_model(model_instance)

    assert model.provider == "anthropic"
    assert model.model_id == "anthropic/claude-sonnet-4-0"
    assert model.params.get("temperature") == 0.7


def test_model_context_accepts_model_instance() -> None:
    """Test that llm.model() accepts a Model instance."""
    model_instance = llm.Model("anthropic/claude-sonnet-4-0", temperature=0.8)

    with llm.model(model_instance) as model:
        assert model.provider == "anthropic"
        assert model.model_id == "anthropic/claude-sonnet-4-0"
        assert model.params.get("temperature") == 0.8
