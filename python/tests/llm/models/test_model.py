"""Tests for the Model class."""

import pytest

from mirascope import llm


def test_cant_use_init() -> None:
    """Test that Models cannot be directly instantiated."""
    with pytest.raises(TypeError, match="llm.model"):
        llm.Model()


def test_create_provides_client() -> None:
    """Test that a client is created for the Model if not provided."""
    test_model = llm.model(provider="openai", model_id="gpt-4o")
    assert isinstance(test_model.client, llm.clients.OpenAIClient)
