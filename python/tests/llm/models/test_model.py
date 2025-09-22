"""Tests for the Model class."""

from unittest.mock import MagicMock

import pytest

from mirascope import llm


def test_cant_use_init() -> None:
    """Test that Models cannot be directly instantiated."""
    with pytest.raises(TypeError, match="llm.model"):
        llm.Model()


def test_client_pulled_from_context_at_call_time() -> None:
    """Test that models get client at call time, not construction time."""
    model = llm.model(provider="openai", model_id="gpt-4o")

    custom_client = llm.OpenAIClient(api_key="test-key")

    mock_call = MagicMock(return_value=MagicMock())
    custom_client.call = mock_call

    with custom_client:
        model.call(messages=[llm.messages.user("Hello")])

    mock_call.assert_called_once()
