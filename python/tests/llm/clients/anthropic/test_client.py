"""Tests for llm.clients.AnthropicClient."""

from mirascope import llm


def test_context_manager() -> None:
    """Test nested context manager behavior and get_client() integration."""

    global_client = llm.get_client("anthropic")

    client1 = llm.client("anthropic", api_key="key1")
    client2 = llm.client("anthropic", api_key="key2")

    assert llm.get_client("anthropic") is global_client

    with client1 as ctx1:
        assert ctx1 is client1
        assert llm.get_client("anthropic") is client1

        with client2 as ctx2:
            assert ctx2 is client2
            assert llm.get_client("anthropic") is client2

        assert llm.get_client("anthropic") is client1

    assert llm.get_client("anthropic") is global_client


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
    client6 = llm.get_client("anthropic")
    assert client5 is client6
