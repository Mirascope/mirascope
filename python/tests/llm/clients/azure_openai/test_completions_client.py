"""Tests for AzureOpenAICompletionsClient"""

import pytest
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice

from mirascope.llm.clients.azure_openai.completions import (
    AzureOpenAICompletionsClient,
    client,
    get_client,
)
from mirascope.llm.clients.openai.completions import _utils


def test_context_manager() -> None:
    """Test nested context manager behavior and get_client() integration."""

    client1 = client(
        api_key="key1",
        base_url="https://test1.openai.azure.com",
    )
    client2 = client(
        api_key="key2",
        base_url="https://test2.openai.azure.com",
    )

    with client1 as ctx1:
        assert ctx1 is client1
        assert get_client() is client1

        with client2 as ctx2:
            assert ctx2 is client2
            assert get_client() is client2

        assert get_client() is client1


def test_client_caching() -> None:
    """Test that client() returns cached instances for identical parameters."""
    client1 = client(
        api_key="test-key",
        base_url="https://test.openai.azure.com",
    )
    client2 = client(
        api_key="test-key",
        base_url="https://test.openai.azure.com",
    )
    assert client1 is client2

    client3 = client(
        api_key="different-key",
        base_url="https://test.openai.azure.com",
    )
    assert client1 is not client3

    client4 = client(
        api_key="test-key",
        base_url="https://different.openai.azure.com",
    )
    assert client1 is not client4


def test_provider_name() -> None:
    """Test that provider returns the correct provider string.

    Included for code coverage.
    """

    client_instance = AzureOpenAICompletionsClient(
        api_key="test-key",
        base_url="https://test.openai.azure.com/openai/v1/",
    )

    assert client_instance.provider == "azure-openai:completions"


def test_assistant_message_provider_attribution() -> None:
    """Test that decode_response sets provider correctly for Azure.

    Included for code coverage.
    """

    openai_response = ChatCompletion(
        id="test-id",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    content="Test response",
                    role="assistant",
                ),
            )
        ],
        created=1234567890,
        model="gpt-4",
        object="chat.completion",
    )

    assistant_message, _ = _utils.decode_response(
        openai_response, "gpt-4", "azure-openai:completions"
    )

    assert assistant_message.provider == "azure-openai:completions"


def test_async_client_requires_credentials() -> None:
    """Async client should raise if no async credentials are configured."""

    def token_provider() -> str:
        return "sync-token"

    client_instance = AzureOpenAICompletionsClient(
        api_key=None,
        base_url="https://test.openai.azure.com/openai/v1/",
        azure_ad_token_provider=token_provider,
    )

    with pytest.raises(RuntimeError, match="Async credentials not configured"):
        _ = client_instance.async_client
