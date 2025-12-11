"""Tests for the Model class."""

import pytest

from mirascope import llm


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


def test_use_model_as_context_manager() -> None:
    """Test that model can be used as a context manager directly."""
    with llm.Model("anthropic/claude-sonnet-4-0"):
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


def test_nested_context_manager_with_same_instance() -> None:
    """Test that the same Model instance can be used in nested contexts.

    Expected behavior: Each nested context should properly manage its own token
    and restore the previous state when exiting.
    """
    model = llm.Model("openai/gpt-4o")

    assert llm.model_from_context() is None

    with model:
        assert llm.model_from_context() is model

        with model:  # Inner context with SAME instance
            assert llm.model_from_context() is model

        assert llm.model_from_context() is model, (
            "Context should still be active after nested exit, but token was lost"
        )

    assert llm.model_from_context() is None
