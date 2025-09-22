"""Tests for llm.clients.AnthropicClient."""

from mirascope import llm


def test_context_manager() -> None:
    """Test nested context manager behavior and get_client() integration."""

    global_client = llm.get_client("anthropic")

    client1 = llm.AnthropicClient(api_key="key1")
    client2 = llm.AnthropicClient(api_key="key2")

    assert llm.get_client("anthropic") is global_client

    with client1 as ctx1:
        assert ctx1 is client1
        assert llm.get_client("anthropic") is client1

        with client2 as ctx2:
            assert ctx2 is client2
            assert llm.get_client("anthropic") is client2

        assert llm.get_client("anthropic") is client1

    assert llm.get_client("anthropic") is global_client
