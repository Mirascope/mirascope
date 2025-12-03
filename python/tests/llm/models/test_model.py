"""Tests for the Model class."""

from unittest.mock import MagicMock

from mirascope import llm


def test_client_pulled_from_context_at_call_time() -> None:
    """Test that models get client at call time, not construction time."""
    model = llm.use_model(provider="openai:completions", model_id="openai/gpt-4o")

    custom_client = llm.client("openai:completions", api_key="test-key")

    mock_call = MagicMock(return_value=MagicMock())
    custom_client.call = mock_call

    with custom_client:
        model.call(messages=[llm.messages.user("Hello")])

    mock_call.assert_called_once()


def test_use_model_without_context() -> None:
    """Test that use_model creates a new Model when no context is set."""
    model = llm.use_model(provider="openai:completions", model_id="openai/gpt-4o")

    assert model.provider == "openai:completions"
    assert model.model_id == "openai/gpt-4o"


def test_use_model_with_context() -> None:
    """Test that use_model returns the context model when one is set."""
    with llm.model(provider="anthropic", model_id="anthropic/claude-sonnet-4-0"):
        model = llm.use_model(provider="openai:completions", model_id="openai/gpt-4o")

        assert model.provider == "anthropic"
        assert model.model_id == "anthropic/claude-sonnet-4-0"


def test_direct_model_instantiation_ignores_context() -> None:
    """Test that direct Model instantiation ignores context (hardcoding behavior)."""
    with llm.model(provider="anthropic", model_id="openai/claude-sonnet-4-0"):
        model = llm.Model(provider="openai:completions", model_id="openai/gpt-4o")

        assert model.provider == "openai:completions"
        assert model.model_id == "openai/gpt-4o"
