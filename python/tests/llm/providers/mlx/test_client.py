"""Tests for llm.providers.MLXProvider."""

from mirascope import llm


def test_client_caching() -> None:
    """Test that client() returns cached instances for identical parameters."""
    client1 = llm.load_provider("mlx")
    client2 = llm.load_provider("mlx")

    assert client1 is client2
