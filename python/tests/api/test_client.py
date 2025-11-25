"""Tests for enhanced Mirascope client interfaces."""

from __future__ import annotations

from collections.abc import Generator

import httpx
import pytest

from mirascope.api.client import (
    AsyncMirascope,
    Mirascope,
    close_cached_clients,
    create_export_client,
    get_async_client,
    get_sync_client,
)
from mirascope.api.settings import settings


@pytest.fixture(autouse=True)
def reset_client_caches() -> Generator[None, None, None]:
    """Ensure cached clients are cleared before and after each test."""
    close_cached_clients()
    yield
    close_cached_clients()


def test_sync_client_requires_api_key() -> None:
    """Test that synchronous client requires an API key when instantiating."""
    with settings(api_key=None), pytest.raises(RuntimeError):
        Mirascope()


@pytest.mark.asyncio
async def test_async_client_requires_api_key() -> None:
    """Test that asynchronous client requires an API key when instantiating."""
    with settings(api_key=None), pytest.raises(RuntimeError):
        AsyncMirascope()


def test_sync_client_updates_provided_httpx_client() -> None:
    """Test that Mirascope updates the headers of a user-supplied HTTPX client."""
    httpx_client = httpx.Client()
    try:
        with settings(api_key=None):
            client = Mirascope(api_key="token-1", httpx_client=httpx_client)

        assert httpx_client.headers["Authorization"] == "Bearer token-1"
        client.close()
    finally:
        httpx_client.close()


@pytest.mark.asyncio
async def test_async_client_updates_provided_httpx_client() -> None:
    """Test that AsyncMirascope updates headers for user-supplied async HTTPX client."""
    httpx_client = httpx.AsyncClient()
    try:
        with settings(api_key=None):
            client = AsyncMirascope(api_key="token-5", httpx_client=httpx_client)

        assert httpx_client.headers["Authorization"] == "Bearer token-5"
        await client.aclose()
    finally:
        await httpx_client.aclose()


def test_get_sync_client_caches_instances() -> None:
    """Test that get_sync_client caches the synchronous singleton client."""
    with settings(api_key="token-2", base_url="https://example.com"):
        first = get_sync_client()
        second = get_sync_client()

    assert first is second
    first.close()


@pytest.mark.asyncio
async def test_get_async_client_caches_instances() -> None:
    """Test that get_async_client caches the asynchronous singleton client."""
    with settings(api_key="token-6"):
        first = get_async_client()
        second = get_async_client()

    assert first is second
    await first.aclose()


def test_get_sync_client_requires_api_key() -> None:
    """Test that get_sync_client raises when requesting without an API key."""
    with settings(api_key=None), pytest.raises(RuntimeError):
        get_sync_client()


@pytest.mark.asyncio
async def test_get_async_client_requires_api_key() -> None:
    """Test that get_async_client raises when requesting without an API key."""
    with settings(api_key=None), pytest.raises(RuntimeError):
        get_async_client()


def test_get_sync_client_handles_invalid_cached_instance() -> None:
    """Test that get_sync_client validates inputs when requesting cached clients."""
    with settings(api_key=""), pytest.raises(RuntimeError):
        get_sync_client(api_key="")


@pytest.mark.asyncio
async def test_get_async_client_handles_invalid_cached_instance() -> None:
    """Test that get_async_client validates inputs when requesting cached clients."""
    with settings(api_key=""), pytest.raises(RuntimeError):
        get_async_client(api_key="")


def test_create_export_client_uses_configuration() -> None:
    """Test that create_export_client respects settings when creating clients."""
    api_key, base_url = "token-3", "https://example.net"
    with settings(api_key=api_key, base_url=base_url):
        export_client = create_export_client(timeout=12.5)

    assert isinstance(export_client, Mirascope)
    assert export_client.api_key == api_key
    assert export_client.base_url == base_url
    export_client.close()


def test_close_cached_clients_resets_sync_singleton() -> None:
    """Test that close_cached_clients resets cached synchronous clients."""
    with settings(api_key="token-4"):
        first = get_sync_client()

    first_id = id(first)
    first.close()
    close_cached_clients()

    with settings(api_key="token-4"):
        second = get_sync_client()

    assert id(second) != first_id
    second.close()


@pytest.mark.asyncio
async def test_close_cached_clients_resets_async_singleton() -> None:
    """Test that close_cached_clients resets cached asynchronous clients."""
    with settings(api_key="token-7"):
        first = get_async_client()

    first_id = id(first)
    await first.aclose()
    close_cached_clients()

    with settings(api_key="token-7"):
        second = get_async_client()

    assert id(second) != first_id
    await second.aclose()


def test_sync_client_default_httpx_configuration() -> None:
    """Test that sync clients expose the default base URL configuration."""
    with settings(api_key="token-8"):
        client = get_sync_client()

    try:
        assert client.base_url == "https://v2.mirascope.com"
    finally:
        client.close()


@pytest.mark.asyncio
async def test_async_client_default_httpx_configuration() -> None:
    """Test that async clients expose the default base URL configuration."""
    with settings(api_key="token-8"):
        client = get_async_client()

    try:
        assert client.base_url == "https://v2.mirascope.com"
    finally:
        await client.aclose()


def test_get_async_client_requires_event_loop() -> None:
    """Test that get_async_client raises when requesting outside an event loop."""
    with pytest.raises(RuntimeError):
        get_async_client()
