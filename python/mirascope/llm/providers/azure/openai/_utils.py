"""Azure OpenAI provider utilities."""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable
from typing import Any, cast

from openai.lib.azure import AsyncAzureADTokenProvider, AzureADTokenProvider


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

    provider = api_key

    def token_provider() -> str:
        token = provider()
        if is_awaitable_str(token):
            raise ValueError(
                "Async Azure token provider is not supported for sync clients."
            )
        if not token or not isinstance(token, str):
            raise ValueError(
                f"Expected Azure token provider to return a string but it returned {token}",
            )
        return token

    return token_provider


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

    provider = api_key

    async def token_provider() -> str:
        token = provider()
        if is_awaitable_str(token):
            token = await cast(Awaitable[str], token)
        if not token or not isinstance(cast(Any, token), str):
            raise ValueError(
                f"Expected Azure token provider to return a string but it returned {token}",
            )
        return str(token)

    return token_provider


def is_awaitable_str(value: object) -> bool:
    """Return True when the value is awaitable."""
    return inspect.isawaitable(value)
