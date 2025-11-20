"""Client interfaces and factory for Mirascope SDK.

This module provides interfaces and factory functions for creating Mirascope clients
that support both the Fern-generated API client and OpenTelemetry exporters.
"""

from __future__ import annotations

import asyncio
import logging
import weakref
from collections.abc import Callable
from functools import lru_cache
from typing import ParamSpec, TypeAlias, TypeVar

import httpx

from ._generated.client import (
    AsyncMirascope as _BaseAsyncMirascope,
    Mirascope as _BaseMirascope,
)
from .settings import get_settings

ApiKey: TypeAlias = str
BaseUrl: TypeAlias = str
Token: TypeAlias = str | Callable[[], str] | None
_P = ParamSpec("_P")
_R = TypeVar("_R")

logger = logging.getLogger(__name__)


class Mirascope(_BaseMirascope):
    """Enhanced Mirascope client with error handling.

    This client automatically handles API errors and provides fallback behavior
    for non-critical failures while preserving important exceptions like NotFoundError.
    """

    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        token: Token = None,
        timeout: float | None = None,
        follow_redirects: bool | None = True,
        httpx_client: httpx.Client | None = None,
    ) -> None:
        """Initialize the enhanced Mirascope client."""
        try:
            settings = get_settings()
            self.api_key = api_key or settings.api_key
            if not self.api_key:
                raise ValueError("`Mirascope` client requires `api_key`.")

            self.base_url = base_url or settings.base_url

            headers = {"Authorization": f"Bearer {self.api_key}"}
            if httpx_client:
                if hasattr(httpx_client, "headers"):
                    httpx_client.headers.update(headers)
            else:
                httpx_client = httpx.Client(
                    headers=headers,
                    timeout=timeout or 30.0,
                    follow_redirects=follow_redirects
                    if follow_redirects is not None
                    else True,
                )

            super().__init__(
                base_url=self.base_url,
                timeout=timeout,
                follow_redirects=follow_redirects,
                httpx_client=httpx_client,
            )

        except Exception as e:
            logger.error("Failed to initialize Mirascope client: %s", e)
            raise RuntimeError(f"Client initialization failed: {e}") from e

    def close(self) -> None:
        """Close the underlying synchronous HTTP client."""
        wrapper_client = getattr(self._client_wrapper, "httpx_client", None)
        underlying_httpx_client = getattr(wrapper_client, "httpx_client", None)
        if underlying_httpx_client is not None:
            underlying_httpx_client.close()


class AsyncMirascope(_BaseAsyncMirascope):
    """Enhanced async Mirascope client with error handling.

    This client automatically handles API errors and provides fallback behavior
    for non-critical failures while preserving important exceptions like NotFoundError.
    """

    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        token: Token = None,
        timeout: float | None = None,
        follow_redirects: bool | None = True,
        httpx_client: httpx.AsyncClient | None = None,
    ) -> None:
        """Initialize the enhanced async Mirascope client."""
        try:
            settings = get_settings()
            self.api_key = api_key or settings.api_key
            if not self.api_key:
                raise ValueError("`AsyncMirascope` client requires `api_key`.")

            self.base_url = base_url or settings.base_url

            headers = {"Authorization": f"Bearer {self.api_key}"}
            if httpx_client:
                if hasattr(httpx_client, "headers"):
                    httpx_client.headers.update(headers)
            else:
                httpx_client = httpx.AsyncClient(
                    headers=headers,
                    timeout=timeout or 30.0,
                    follow_redirects=follow_redirects
                    if follow_redirects is not None
                    else True,
                )

            super().__init__(
                base_url=self.base_url,
                timeout=timeout,
                follow_redirects=follow_redirects,
                httpx_client=httpx_client,
            )

        except Exception as e:
            logger.error("Failed to initialize AsyncMirascope client: %s", e)
            raise RuntimeError(f"Async client initialization failed: {e}") from e

    async def aclose(self) -> None:
        """Close the underlying asynchronous HTTP client."""
        wrapper_client = getattr(self._client_wrapper, "httpx_client", None)
        underlying_httpx_client = getattr(wrapper_client, "httpx_client", None)
        if underlying_httpx_client is not None:
            await underlying_httpx_client.aclose()


@lru_cache(maxsize=256)
def _sync_singleton(api_key: str | None, base_url: str | None) -> Mirascope:
    """Return the process-wide synchronous client, creating one if none yet exists"""
    try:
        logger.debug("Creating sync client with api_key=*****, base_url=%s", base_url)
        return Mirascope(api_key=api_key, base_url=base_url)
    except Exception as e:
        logger.error("Failed to create singleton Mirascope client: %s", e)
        raise RuntimeError(f"Failed to create cached client: {e}") from e


def get_sync_client(
    api_key: str | None = None,
    base_url: str | None = None,
) -> Mirascope:
    """Get or create a cached synchronous client.

    Args:
        api_key: API key for authentication
        base_url: Base URL for the API

    Returns:
        Cached Mirascope client instance
    """
    settings = get_settings()

    return _sync_singleton(
        api_key or settings.api_key,
        base_url or settings.base_url,
    )


@lru_cache(maxsize=256)
def _async_singleton(
    _loop_id_for_cache: int, api_key: str | None, base_url: str | None
) -> AsyncMirascope:
    """Return the loop-specific asynchronous client, creating one if none yet exists"""
    try:
        logger.debug("Creating async client with api_key=*****, base_url=%s", base_url)
        loop = asyncio.get_running_loop()
        client = AsyncMirascope(api_key=api_key, base_url=base_url)
        weakref.finalize(loop, _async_singleton.cache_clear)
        return client
    except Exception as e:
        logger.error("Failed to create singleton AsyncMirascope client: %s", e)
        raise RuntimeError(f"Failed to create cached async client: {e}") from e


def get_async_client(
    api_key: str | None = None,
    base_url: str | None = None,
) -> AsyncMirascope:
    """Get or create a cached asynchronous client.

    Args:
        api_key: API key for authentication
        base_url: Base URL for the API

    Returns:
        Cached AsyncMirascope client instance
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError as exc:
        raise RuntimeError(
            "get_async_client() must be called from within an active event loop."
        ) from exc

    settings = get_settings()

    return _async_singleton(
        id(loop),
        api_key or settings.api_key,
        base_url or settings.base_url,
    )


def create_export_client(
    *,
    base_url: str | None = None,
    api_key: str | None = None,
    timeout: float = 30.0,
    httpx_client: httpx.Client | None = None,
) -> Mirascope:
    """Create a client suitable for OpenTelemetry export.

    Args:
        base_url: Base URL for the API
        api_key: API key for authentication
        timeout: Request timeout in seconds
        httpx_client: Optional custom httpx client

    Returns:
        Mirascope client configured for export use
    """
    return Mirascope(
        base_url=base_url,
        api_key=api_key,
        timeout=timeout,
        httpx_client=httpx_client,
    )


def close_cached_clients() -> None:
    """Close all cached client instances."""
    _sync_singleton.cache_clear()
    _async_singleton.cache_clear()
