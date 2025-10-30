"""Azure OpenAI Responses API client implementation."""

import os
from contextvars import ContextVar
from functools import lru_cache
from typing import Literal

from openai import AsyncAzureOpenAI, AzureOpenAI
from openai.lib.azure import AzureADTokenProvider

from ...openai.responses.base_client import BaseOpenAIResponsesClient

AZURE_OPENAI_RESPONSES_CLIENT_CONTEXT: ContextVar[
    "AzureOpenAIResponsesClient | None"
] = ContextVar("AZURE_OPENAI_RESPONSES_CLIENT_CONTEXT", default=None)


@lru_cache(maxsize=256)
def _azure_responses_singleton(
    api_key: str | None,
    base_url: str,
    azure_api_version: str,
    azure_ad_token_provider: AzureADTokenProvider | None,
) -> "AzureOpenAIResponsesClient":
    """Return a cached AzureOpenAIResponsesClient instance for the given parameters."""
    return AzureOpenAIResponsesClient(
        api_key=api_key,
        base_url=base_url,
        azure_api_version=azure_api_version,
        azure_ad_token_provider=azure_ad_token_provider,
    )


def client(
    *,
    api_key: str | None = None,
    base_url: str | None = None,
    azure_api_version: str | None = None,
    azure_ad_token_provider: AzureADTokenProvider | None = None,
) -> "AzureOpenAIResponsesClient":
    """Return an `AzureOpenAIResponsesClient`.

    Args:
        api_key: Azure OpenAI API key. If None, uses AZURE_OPENAI_API_KEY env var.
        base_url: Azure OpenAI endpoint URL (e.g., "https://your-resource.openai.azure.com").
            If None, uses AZURE_OPENAI_ENDPOINT env var.
        azure_api_version: Azure OpenAI API version. If None, defaults to "2025-03-01-preview".
            Reads from AZURE_OPENAI_API_VERSION env var if not specified.

            **IMPORTANT**: Responses API requires "2025-03-01-preview" or later.
            Earlier versions will result in 400 Bad Request errors.

            Common values:
            - "2025-03-01-preview" (default, minimum required for Responses API)
            - "2025-04-01-preview" (newer preview features)
            - "preview" (v1 preview route via /openai/v1/ path)
        azure_ad_token_provider: Optional Azure AD token provider for authentication.

    Returns:
        An `AzureOpenAIResponsesClient` instance.

    Notes:
        The Responses API is only available in api-version 2025-03-01-preview and later.
        See: https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/responses

        Microsoft's next-gen v1 API (GA since August 2025) eliminates monthly version
        updates, but the Python SDK still requires explicit azure_api_version as of October 2025.
        When future SDK versions support it, you'll be able to omit azure_api_version entirely.

    Examples:
        # Use default version
        client = client(
            api_key="your-key",
            base_url="https://your-resource.openai.azure.com"
        )

        # Use specific version
        client = client(
            api_key="your-key",
            base_url="https://your-resource.openai.azure.com",
            azure_api_version="2025-04-01-preview"
        )
    """
    api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
    resolved_base_url = base_url or os.getenv("AZURE_OPENAI_ENDPOINT")
    resolved_api_version = (
        azure_api_version
        or os.getenv("AZURE_OPENAI_API_VERSION")
        or "2025-03-01-preview"
    )

    if resolved_base_url is None:
        raise ValueError(
            "base_url is required. "
            "Set AZURE_OPENAI_ENDPOINT environment variable or pass base_url explicitly."
        )

    return _azure_responses_singleton(
        api_key,
        resolved_base_url,
        resolved_api_version,
        azure_ad_token_provider,
    )


def clear_cache() -> None:
    """Clear the cached Azure OpenAI Responses client singletons."""
    _azure_responses_singleton.cache_clear()


def get_client() -> "AzureOpenAIResponsesClient":
    """Get the current `AzureOpenAIResponsesClient` from context."""
    current_client = AZURE_OPENAI_RESPONSES_CLIENT_CONTEXT.get()
    if current_client is None:
        current_client = client()
        AZURE_OPENAI_RESPONSES_CLIENT_CONTEXT.set(current_client)
    return current_client


class AzureOpenAIResponsesClient(
    BaseOpenAIResponsesClient[
        AzureOpenAI, AsyncAzureOpenAI, "AzureOpenAIResponsesClient"
    ]
):
    """Azure OpenAI Responses client that inherits from BaseOpenAIResponsesClient.

    Only overrides initialization to use Azure-specific SDK classes and
    provider naming to return 'azure-openai:responses'.
    """

    @property
    def _context_var(self) -> ContextVar["AzureOpenAIResponsesClient | None"]:
        return AZURE_OPENAI_RESPONSES_CLIENT_CONTEXT

    @property
    def provider(self) -> Literal["azure-openai:responses"]:
        """Return the provider name for Azure OpenAI Responses."""
        return "azure-openai:responses"

    def __init__(
        self,
        *,
        api_key: str | None,
        base_url: str,
        azure_api_version: str,
        azure_ad_token_provider: AzureADTokenProvider | None = None,
    ) -> None:
        """Initialize the Azure OpenAI Responses client.

        Args:
            api_key: Azure OpenAI API key.
            base_url: Azure OpenAI endpoint URL (e.g., "https://your-resource.openai.azure.com").
            azure_api_version: Azure OpenAI API version (e.g., "2024-10-21", "2025-04-01-preview").
                The OpenAI SDK requires this to be specified.
            azure_ad_token_provider: Optional Azure AD token provider for authentication.

        Notes:
            The current OpenAI SDK requires azure_api_version to be specified. Future versions
            may support omitting it to use Microsoft's v1 GA API (/openai/v1/ path).
        """
        self.client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=base_url,
            api_version=azure_api_version,
            azure_ad_token_provider=azure_ad_token_provider,
        )
        self.async_client = AsyncAzureOpenAI(
            api_key=api_key,
            azure_endpoint=base_url,
            api_version=azure_api_version,
            azure_ad_token_provider=azure_ad_token_provider,
        )
