"""Azure Anthropic provider utilities."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, cast

from .._utils import (
    normalize_base_url,
    wrap_async_token_provider,
    wrap_sync_token_provider,
)
from ..model_id import AzureModelId

if TYPE_CHECKING:
    from anthropic.lib.foundry import AzureADTokenProvider

__all__ = ["normalize_base_url"]


def azure_model_name(model_id: AzureModelId) -> str:
    """Extract the Azure deployment name from the model ID."""
    return model_id.removeprefix("azure/anthropic/").removeprefix("azure/")


def coerce_sync_token_provider(
    azure_ad_token_provider: AzureADTokenProvider | None,
) -> Callable[[], str] | None:
    """Coerce Azure AD token providers for synchronous Anthropic clients.

    Only synchronous token providers are supported.

    Args:
        azure_ad_token_provider: Synchronous Azure AD token provider.

    Returns:
        A wrapped sync token provider.

    Raises:
        ValueError: If the provider returns an awaitable or non-string token.
    """
    if azure_ad_token_provider is None:
        return None

    provider = cast(Callable[[], str | Awaitable[str]], azure_ad_token_provider)
    return wrap_sync_token_provider(provider)


def coerce_async_token_provider(
    sync_token_provider: Callable[[], str] | None,
) -> Callable[[], Awaitable[str]] | None:
    """Coerce Azure AD token providers for asynchronous Anthropic clients.

    Takes a validated sync token provider and wraps it for async use.

    Args:
        sync_token_provider: Synchronous Azure AD token provider.

    Returns:
        A wrapped async token provider.
    """
    if sync_token_provider is None:
        return None

    return wrap_async_token_provider(sync_token_provider)
