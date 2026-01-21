"""Azure OpenAI provider utilities."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import cast

from openai.lib.azure import AsyncAzureADTokenProvider, AzureADTokenProvider

from .._utils import wrap_async_token_provider, wrap_sync_token_provider


def coerce_sync_token_provider(
    api_key: str | AzureADTokenProvider | AsyncAzureADTokenProvider | None,
) -> str | AzureADTokenProvider | None:
    """Coerce Azure AD token providers for synchronous OpenAI clients.

    Args:
        api_key: API key string or Azure AD token provider.

    Returns:
        The API key string or a wrapped sync token provider.

    Raises:
        ValueError: If the provider returns an awaitable or non-string token.
    """
    if api_key is None or isinstance(api_key, str):
        return api_key

    provider = cast(Callable[[], str | Awaitable[str]], api_key)
    return wrap_sync_token_provider(provider)


def coerce_async_token_provider(
    api_key: str | AzureADTokenProvider | AsyncAzureADTokenProvider | None,
) -> str | Callable[[], Awaitable[str]] | None:
    """Coerce Azure AD token providers for asynchronous OpenAI clients.

    Args:
        api_key: API key string or Azure AD token provider.

    Returns:
        The API key string or a wrapped async token provider.

    Raises:
        ValueError: If the provider returns an empty or non-string token.
    """
    if api_key is None or isinstance(api_key, str):
        return api_key

    provider = cast(Callable[[], str | Awaitable[str]], api_key)
    return wrap_async_token_provider(provider)
