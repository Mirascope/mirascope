"""Azure OpenAI Responses API client implementation."""

import os
from collections.abc import Awaitable
from contextvars import ContextVar
from functools import lru_cache
from typing import Literal, Protocol

from openai import AsyncOpenAI, OpenAI

from ...openai.responses.base_openai_responses_client import (
    BaseOpenAIResponsesClient,
)


class SyncAzureADTokenProvider(Protocol):
    """Protocol describing a sync Azure AD token provider."""

    def __call__(self) -> str: ...


class AsyncAzureADTokenProvider(Protocol):
    """Protocol describing an async Azure AD token provider."""

    def __call__(self) -> Awaitable[str]: ...


AZURE_OPENAI_RESPONSES_CLIENT_CONTEXT: ContextVar[
    "AzureOpenAIResponsesClient | None"
] = ContextVar("AZURE_OPENAI_RESPONSES_CLIENT_CONTEXT", default=None)


@lru_cache(maxsize=256)
def _azure_responses_singleton(
    api_key: str,
    base_url: str,
) -> "AzureOpenAIResponsesClient":
    """Return a cached AzureOpenAIResponsesClient instance for the given parameters."""
    return AzureOpenAIResponsesClient(
        api_key=api_key,
        base_url=base_url,
    )


def client(
    *,
    api_key: str | None = None,
    base_url: str | None = None,
    azure_ad_token_provider: SyncAzureADTokenProvider | None = None,
    azure_ad_token_provider_async: AsyncAzureADTokenProvider | None = None,
) -> "AzureOpenAIResponsesClient":
    """Return an `AzureOpenAIResponsesClient`.

    Args:
        api_key: Azure OpenAI API key. If None, uses AZURE_OPENAI_API_KEY env var.
            Ignored if azure_ad_token_provider is provided.
        base_url: Azure OpenAI endpoint URL (e.g., "https://your-resource.openai.azure.com").
            If None, uses AZURE_OPENAI_ENDPOINT env var.
        azure_ad_token_provider: Optional Azure AD token provider for sync client.
            Should be created using `azure.identity.get_bearer_token_provider()`.
            When provided, this takes precedence over api_key for sync operations.
        azure_ad_token_provider_async: Optional Azure AD token provider for async client.
            Should be created using `azure.identity.aio.get_bearer_token_provider()`.
            When provided, this takes precedence over api_key for async operations.

    Returns:
        An `AzureOpenAIResponsesClient` instance.

    Notes:
        This client uses Azure OpenAI's v1 GA API (released August 2025) via the
        standard OpenAI SDK. The v1 API eliminates monthly version updates and
        uses the `/openai/v1/` path instead of dated API versions.

        See: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/api-version-lifecycle

    Examples:
        # API key authentication
        client = client(
            api_key="your-key",
            base_url="https://your-resource.openai.azure.com"
        )

        # Azure AD authentication (keyless) - sync only
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider

        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://cognitiveservices.azure.com/.default"
        )
        client = client(
            base_url="https://your-resource.openai.azure.com",
            azure_ad_token_provider=token_provider
        )

        # Azure AD authentication (keyless) - both sync and async
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider
        from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential
        from azure.identity.aio import get_bearer_token_provider as get_bearer_token_provider_async

        sync_token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://cognitiveservices.azure.com/.default"
        )
        async_token_provider = get_bearer_token_provider_async(
            AsyncDefaultAzureCredential(),
            "https://cognitiveservices.azure.com/.default"
        )
        client = client(
            base_url="https://your-resource.openai.azure.com",
            azure_ad_token_provider=sync_token_provider,
            azure_ad_token_provider_async=async_token_provider
        )
    """
    endpoint = base_url or os.getenv("AZURE_OPENAI_ENDPOINT")

    if endpoint is None:
        raise ValueError(
            "base_url is required. "
            "Set AZURE_OPENAI_ENDPOINT environment variable or pass base_url explicitly."
        )

    resolved_base_url = endpoint.rstrip("/") + "/openai/v1/"

    if azure_ad_token_provider is not None or azure_ad_token_provider_async is not None:
        return AzureOpenAIResponsesClient(
            api_key=api_key,
            base_url=resolved_base_url,
            azure_ad_token_provider=azure_ad_token_provider,
            azure_ad_token_provider_async=azure_ad_token_provider_async,
        )

    resolved_api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
    if resolved_api_key is None:
        raise ValueError(
            "api_key is required. Set AZURE_OPENAI_API_KEY or pass api_key explicitly."
        )

    return _azure_responses_singleton(
        resolved_api_key,
        resolved_base_url,
    )


def clear_cache() -> None:
    """Clear the cached Azure OpenAI Responses client singletons and reset context."""
    _azure_responses_singleton.cache_clear()
    AZURE_OPENAI_RESPONSES_CLIENT_CONTEXT.set(None)


def get_client() -> "AzureOpenAIResponsesClient":
    """Get the current `AzureOpenAIResponsesClient` from context."""
    current_client = AZURE_OPENAI_RESPONSES_CLIENT_CONTEXT.get()
    if current_client is None:
        current_client = client()
        AZURE_OPENAI_RESPONSES_CLIENT_CONTEXT.set(current_client)
    return current_client


class AzureOpenAIResponsesClient(
    BaseOpenAIResponsesClient[OpenAI, AsyncOpenAI, "AzureOpenAIResponsesClient"]
):
    """Azure OpenAI Responses client using the v1 GA API.

    Uses the standard OpenAI SDK client with Azure OpenAI's v1 GA API endpoint.
    The v1 API eliminates monthly version updates.
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
        azure_ad_token_provider: SyncAzureADTokenProvider | None = None,
        azure_ad_token_provider_async: AsyncAzureADTokenProvider | None = None,
    ) -> None:
        """Initialize the Azure OpenAI Responses client.

        Args:
            api_key: Azure OpenAI API key.
            base_url: Azure OpenAI base URL with /openai/v1/ path appended.
            azure_ad_token_provider: Optional Azure AD token provider for sync client.
            azure_ad_token_provider_async: Optional Azure AD token provider for async client.

        Notes:
            This client uses Azure OpenAI's v1 GA API via the standard OpenAI SDK.
            The base_url should already include the /openai/v1/ path.

            The OpenAI SDK accepts either a string API key or a token provider callable
            for the api_key parameter, enabling both API key and Azure AD authentication.
        """
        if (
            api_key is None
            and azure_ad_token_provider is None
            and azure_ad_token_provider_async is None
        ):
            raise ValueError(
                "api_key, azure_ad_token_provider, or azure_ad_token_provider_async "
                "is required."
            )

        self._api_key = api_key
        self._sync_token_provider = azure_ad_token_provider
        self._async_token_provider = azure_ad_token_provider_async
        self._base_url = base_url
        self._sync_client_instance: OpenAI | None = None
        self._async_client_instance: AsyncOpenAI | None = None

    def _resolve_sync_credential(self) -> str | SyncAzureADTokenProvider:
        credential = self._sync_token_provider or self._api_key
        if credential is None:
            raise RuntimeError(
                "Sync credentials not configured; provide api_key or azure_ad_token_provider."
            )
        return credential

    def _resolve_async_credential(self) -> str | AsyncAzureADTokenProvider:
        credential = self._async_token_provider or self._api_key
        if credential is None:
            raise RuntimeError(
                "Async credentials not configured; provide api_key or azure_ad_token_provider_async."
            )
        return credential

    @property
    def client(self) -> OpenAI:
        if self._sync_client_instance is None:
            self._sync_client_instance = OpenAI(
                api_key=self._resolve_sync_credential(),
                base_url=self._base_url,
            )
        return self._sync_client_instance

    @client.setter
    def client(self, value: OpenAI) -> None:
        self._sync_client_instance = value

    @property
    def async_client(self) -> AsyncOpenAI:
        if self._async_client_instance is None:
            self._async_client_instance = AsyncOpenAI(
                api_key=self._resolve_async_credential(),
                base_url=self._base_url,
            )
        return self._async_client_instance

    @async_client.setter
    def async_client(self, value: AsyncOpenAI) -> None:
        self._async_client_instance = value
