"""Anthropic client implementation."""

import os
from contextvars import ContextVar
from functools import lru_cache
from typing import Literal

from anthropic import Anthropic, AsyncAnthropic

from .base_client import BaseAnthropicClient

ANTHROPIC_CLIENT_CONTEXT: ContextVar["AnthropicClient | None"] = ContextVar(
    "ANTHROPIC_CLIENT_CONTEXT", default=None
)


@lru_cache(maxsize=256)
def _anthropic_singleton(
    api_key: str | None, base_url: str | None
) -> "AnthropicClient":
    """Return a cached Anthropic client instance for the given parameters."""
    return AnthropicClient(api_key=api_key, base_url=base_url)


def client(
    *, api_key: str | None = None, base_url: str | None = None
) -> "AnthropicClient":
    """Create or retrieve an Anthropic client with the given parameters.

    If a client has already been created with these parameters, it will be
    retrieved from cache and returned.

    Args:
        api_key: API key for authentication. If None, uses ANTHROPIC_API_KEY env var.
        base_url: Base URL for the API. If None, uses ANTHROPIC_BASE_URL env var.

    Returns:
        An Anthropic client instance.
    """
    api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
    base_url = base_url or os.getenv("ANTHROPIC_BASE_URL")
    return _anthropic_singleton(api_key, base_url)


def clear_cache() -> None:
    """Clear the cached Anthropic client singletons."""
    _anthropic_singleton.cache_clear()


def get_client() -> "AnthropicClient":
    """Retrieve the current Anthropic client from context, or a global default.

    Returns:
        The current Anthropic client from context if available, otherwise
        a global default client based on environment variables.
    """
    ctx_client = ANTHROPIC_CLIENT_CONTEXT.get()
    return ctx_client or client()


class AnthropicClient(
    BaseAnthropicClient[Anthropic, AsyncAnthropic, "AnthropicClient"]
):
    """Anthropic client that inherits from BaseAnthropicClient.

    Only overrides initialization to use Anthropic-specific SDK classes and
    provider naming to return 'anthropic'.
    """

    @property
    def _context_var(self) -> ContextVar["AnthropicClient | None"]:
        return ANTHROPIC_CLIENT_CONTEXT

    @property
    def provider(self) -> Literal["anthropic"]:
        """Return the provider name for this client."""
        return "anthropic"

    def __init__(
        self, *, api_key: str | None = None, base_url: str | None = None
    ) -> None:
        """Initialize the Anthropic client."""
        self.client = Anthropic(api_key=api_key, base_url=base_url)
        self.async_client = AsyncAnthropic(api_key=api_key, base_url=base_url)
