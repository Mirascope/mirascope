"""Tests for provider get_client functions."""

import os

import pytest

from mirascope import llm


def test_get_client_anthropic() -> None:
    """Test that get_client('anthropic') returns same instance on multiple calls."""
    client1 = llm.get_client("anthropic")
    client2 = llm.get_client("anthropic")

    assert isinstance(client1, llm.clients.AnthropicClient)
    assert client1 is client2
    assert client1.client.api_key == os.getenv("ANTHROPIC_API_KEY")


def test_get_client_anthropic_bedrock() -> None:
    """Test that get_client('anthropic-bedrock') returns same instance on multiple calls."""
    client1 = llm.get_client("anthropic-bedrock")
    client2 = llm.get_client("anthropic-bedrock")

    assert isinstance(client1, llm.clients.AnthropicBedrockClient)
    assert client1 is client2


def test_client_anthropic_bedrock_with_params() -> None:
    """Test that client('anthropic-bedrock', ...) returns cached instances."""
    client1 = llm.client(
        "anthropic-bedrock",
        aws_region="us-west-2",
        aws_profile="test-profile",
    )
    client2 = llm.client(
        "anthropic-bedrock",
        aws_region="us-west-2",
        aws_profile="test-profile",
    )

    assert isinstance(client1, llm.clients.AnthropicBedrockClient)
    assert client1 is client2


def test_get_client_google() -> None:
    """Test that get_client('google') returns same instance on multiple calls."""
    client1 = llm.get_client("google")
    client2 = llm.get_client("google")

    assert isinstance(client1, llm.clients.GoogleClient)
    assert client1 is client2
    assert client1.client._api_client.api_key == os.getenv("GOOGLE_API_KEY")


def test_get_client_openai() -> None:
    """Test that get_client('openai') returns same instance on multiple calls."""
    client1 = llm.get_client("openai:completions")
    client2 = llm.get_client("openai:completions")

    assert isinstance(client1, llm.clients.OpenAICompletionsClient)
    assert client1 is client2
    assert client1.client.api_key == os.getenv("OPENAI_API_KEY")


def test_get_client_openai_responses() -> None:
    """Test that get_client('openai:responses') returns same instance on multiple calls."""
    client1 = llm.get_client("openai:responses")
    client2 = llm.get_client("openai:responses")

    assert isinstance(client1, llm.clients.OpenAIResponsesClient)
    assert client1 is client2
    assert client1.client.api_key == os.getenv("OPENAI_API_KEY")


def test_get_client_azure_completions() -> None:
    """Test that get_client('azure-openai:completions') returns same instance on multiple calls."""
    old_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    old_api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    os.environ["AZURE_OPENAI_ENDPOINT"] = "https://test.openai.azure.com"
    os.environ["AZURE_OPENAI_API_KEY"] = "test-key"

    try:
        client1 = llm.get_client("azure-openai:completions")
        client2 = llm.get_client("azure-openai:completions")

        assert isinstance(client1, llm.clients.AzureOpenAICompletionsClient)
        assert client1 is client2
    finally:
        if old_endpoint:
            os.environ["AZURE_OPENAI_ENDPOINT"] = old_endpoint
        else:
            os.environ.pop("AZURE_OPENAI_ENDPOINT", None)
        if old_api_key:
            os.environ["AZURE_OPENAI_API_KEY"] = old_api_key
        else:
            os.environ.pop("AZURE_OPENAI_API_KEY", None)


def test_get_client_azure_responses() -> None:
    """Test that get_client('azure-openai:responses') returns same instance on multiple calls."""
    old_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    old_api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    os.environ["AZURE_OPENAI_ENDPOINT"] = "https://test.openai.azure.com"
    os.environ["AZURE_OPENAI_API_KEY"] = "test-key"

    try:
        client1 = llm.get_client("azure-openai:responses")
        client2 = llm.get_client("azure-openai:responses")

        assert isinstance(client1, llm.clients.AzureOpenAIResponsesClient)
        assert client1 is client2
    finally:
        if old_endpoint:
            os.environ["AZURE_OPENAI_ENDPOINT"] = old_endpoint
        else:
            os.environ.pop("AZURE_OPENAI_ENDPOINT", None)
        if old_api_key:
            os.environ["AZURE_OPENAI_API_KEY"] = old_api_key
        else:
            os.environ.pop("AZURE_OPENAI_API_KEY", None)


def test_client_azure_completions_with_params() -> None:
    """Test that client('azure-openai:completions', ...) returns cached instances."""
    client1 = llm.client(
        "azure-openai:completions",
        api_key="test-key",
        base_url="https://test.openai.azure.com",
        azure_api_version="2024-10-21",
    )
    client2 = llm.client(
        "azure-openai:completions",
        api_key="test-key",
        base_url="https://test.openai.azure.com",
        azure_api_version="2024-10-21",
    )

    assert isinstance(client1, llm.clients.AzureOpenAICompletionsClient)
    assert client1 is client2


def test_client_azure_responses_with_params() -> None:
    """Test that client('azure-openai:responses', ...) returns cached instances."""
    client1 = llm.client(
        "azure-openai:responses",
        api_key="test-key",
        base_url="https://test.openai.azure.com",
        azure_api_version="2024-10-21",
    )
    client2 = llm.client(
        "azure-openai:responses",
        api_key="test-key",
        base_url="https://test.openai.azure.com",
        azure_api_version="2024-10-21",
    )

    assert isinstance(client1, llm.clients.AzureOpenAIResponsesClient)
    assert client1 is client2


def test_client_azure_missing_endpoint() -> None:
    """Test that client() raises ValueError when base_url is missing."""
    old_endpoint = os.environ.pop("AZURE_OPENAI_ENDPOINT", None)

    try:
        with pytest.raises(
            ValueError,
            match="base_url is required\\. Set AZURE_OPENAI_ENDPOINT environment variable or pass base_url explicitly\\.",
        ):
            llm.client("azure-openai:completions", api_key="test-key")

        with pytest.raises(
            ValueError,
            match="base_url is required\\. Set AZURE_OPENAI_ENDPOINT environment variable or pass base_url explicitly\\.",
        ):
            llm.client("azure-openai:responses", api_key="test-key")
    finally:
        if old_endpoint:
            os.environ["AZURE_OPENAI_ENDPOINT"] = old_endpoint


def test_get_client_unknown_provider() -> None:
    """Test that get_client raises ValueError for unknown providers."""
    with pytest.raises(ValueError, match="Unknown provider: unknown"):
        llm.get_client("unknown")  # type: ignore
