"""Tests for llm.clients.AnthropicClient."""

from mirascope import llm


def test_client_caching() -> None:
    """Test that client() returns cached instances for identical parameters."""
    client1 = llm.client(
        "anthropic", api_key="test-key", base_url="https://api.example.com"
    )
    client2 = llm.client(
        "anthropic", api_key="test-key", base_url="https://api.example.com"
    )
    assert client1 is client2

    client3 = llm.client(
        "anthropic", api_key="different-key", base_url="https://api.example.com"
    )
    assert client1 is not client3

    client4 = llm.client(
        "anthropic", api_key="test-key", base_url="https://different.example.com"
    )
    assert client1 is not client4

    client5 = llm.client("anthropic", api_key=None, base_url=None)
    client6 = llm.client("anthropic")
    assert client5 is client6
