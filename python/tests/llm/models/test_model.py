"""Tests for the Model class."""

from unittest.mock import MagicMock

from mirascope import llm


def test_client_pulled_from_context_at_call_time() -> None:
    """Test that models get client at call time, not construction time."""
    model = llm.model(provider="openai", model_id="gpt-4o")

    custom_client = llm.client("openai", api_key="test-key")

    mock_call = MagicMock(return_value=MagicMock())
    custom_client.call = mock_call

    with custom_client:
        model.call(messages=[llm.messages.user("Hello")])

    mock_call.assert_called_once()
