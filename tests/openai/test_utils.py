"""Tests for Mirascope's OpenAI utils module."""

from openai import AsyncAzureOpenAI, AsyncOpenAI, AzureOpenAI, OpenAI

from mirascope.openai.utils import azure_client_wrapper


def test_azure_client_wrapper():
    """Tests the OpenAI client wrapper for Microsoft Azure."""
    kwargs = {
        "azure_endpoint": "TEST_AZURE_ENDPOINT",
        "azure_deployment": "TEST_AZURE_DEPLOYMENT",
        "api_version": "TEST_API_VERSION",
        "api_key": "TEST_API_KEY",
        "azure_ad_token": "TEST_AZURE_AD_TOKEN",
        "azure_ad_token_provider": None,
        "organization": "TEST_ORGANIZATION",
    }
    wrapper = azure_client_wrapper(**kwargs)
    client = OpenAI()
    wrapped_client = wrapper(client)
    assert isinstance(wrapped_client, AzureOpenAI)
    async_client = AsyncOpenAI()
    wrapped_async_client = wrapper(async_client)
    assert isinstance(wrapped_async_client, AsyncAzureOpenAI)
    kwargs.pop("azure_endpoint")
    kwargs.pop("azure_deployment")
    kwargs["base_url"] = "TEST_AZURE_ENDPOINT/openai/deployments/TEST_AZURE_DEPLOYMENT/"
    kwargs["_api_version"] = kwargs.pop("api_version")
    kwargs["_azure_ad_token"] = kwargs.pop("azure_ad_token")
    kwargs["_azure_ad_token_provider"] = kwargs.pop("azure_ad_token_provider")
    for key, value in kwargs.items():
        assert getattr(wrapped_client, key) == value
        assert getattr(wrapped_async_client, key) == value
