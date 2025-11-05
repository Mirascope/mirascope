"""Test context manager behavior for Azure OpenAI clients."""

from mirascope.llm.clients.openai.azure_completions import client, get_client


def test_get_client_with_context() -> None:
    """Test that get_client() returns the client from context when set.

    Included for code coverage.
    """
    client1 = client(
        api_key="key1",
        base_url="https://test1.openai.azure.com",
    )

    with client1:
        assert get_client() is client1
