"""Tests for llm.clients.MLXClient."""

from mirascope import llm


def test_client_caching() -> None:
    """Test that client() returns cached instances for identical parameters."""
    client1 = llm.client("mlx")
    client2 = llm.client("mlx")

    assert client1 is client2
