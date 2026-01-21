"""Shared Azure provider utilities."""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable


def normalize_base_url(base_url: str, *, suffix: str | None = None) -> str:
    """Normalize Azure endpoint URLs to include the expected suffix and trailing slash."""
    normalized = base_url.rstrip("/")
    if suffix:
        normalized_suffix = suffix.strip("/")
        if not normalized.endswith(f"/{normalized_suffix}") and not normalized.endswith(
            normalized_suffix
        ):
            normalized = f"{normalized}/{normalized_suffix}"
    return f"{normalized}/"


def _validate_token(token: object) -> str:
    if not token or not isinstance(token, str):
        raise ValueError(
            f"Expected Azure token provider to return a string but it returned {token}",
        )
    return token


def wrap_sync_token_provider(
    provider: Callable[[], str | Awaitable[str]],
) -> Callable[[], str]:
    """Wrap a token provider for synchronous Azure clients."""

    def token_provider() -> str:
        token = provider()
        if inspect.isawaitable(token):
            raise ValueError(
                "Async Azure token provider is not supported for sync clients."
            )
        return _validate_token(token)

    return token_provider


def wrap_async_token_provider(
    provider: Callable[[], str | Awaitable[str]],
) -> Callable[[], Awaitable[str]]:
    """Wrap a token provider for asynchronous Azure clients."""

    async def token_provider() -> str:
        token = provider()
        if inspect.isawaitable(token):
            token = await token
        return _validate_token(token)

    return token_provider


def default_anthropic_scopes() -> list[str]:
    """Return default Azure Anthropic routing scopes."""
    return list(
        {
            "azure/azureml://registries/azureml-anthropic/",
            "azure/anthropic/",
        }
    )
