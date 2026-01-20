"""Utility functions for Mirascope Router provider."""

import os
from typing import cast

from ..base import Provider
from ..provider_id import ProviderId


def extract_model_scope(model_id: str) -> str | None:
    """Extract model scope from model ID.

    Args:
        model_id: Model identifier in the format "scope/model-name"
                  e.g., "openai/gpt-4", "anthropic/claude-3", "google/gemini-pro"

    Returns:
        The model scope (e.g., "openai", "anthropic", "google") or None if invalid format.
    """
    if "/" not in model_id:
        return None
    return model_id.split("/", 1)[0]


def get_default_router_base_url() -> str:
    """Get the default router base URL from environment or use default.

    Returns:
        The router base URL (without trailing provider path).
    """
    return os.environ.get(
        "MIRASCOPE_ROUTER_BASE_URL", "https://mirascope.com/router/v2"
    )


def create_underlying_provider(
    model_scope: str, api_key: str, router_base_url: str
) -> Provider:
    """Create and cache an underlying provider instance using provider_singleton.

    This function constructs the appropriate router URL for the provider and
    delegates to provider_singleton for caching and instantiation.

    Args:
        model_scope: The model scope (e.g., "openai", "anthropic", "google")
        api_key: The API key to use for authentication
        router_base_url: The base router URL (e.g., "http://mirascope.com/router/v2")

    Returns:
        A cached provider instance configured for the Mirascope Router.

    Raises:
        ValueError: If the provider is unsupported.
    """
    if model_scope not in ["anthropic", "google", "openai"]:
        raise ValueError(
            f"Unsupported provider: {model_scope}. "
            f"Mirascope Router currently supports: anthropic, google, openai"
        )

    base_url = f"{router_base_url}/{model_scope}"
    if model_scope == "openai":  # OpenAI expects /v1, which their SDK doesn't add
        base_url = f"{base_url}/v1"

    # Lazy import to avoid circular dependencies
    from ..provider_registry import provider_singleton

    # Use provider_singleton which provides caching
    return provider_singleton(
        cast(ProviderId, model_scope),
        api_key=api_key,
        base_url=base_url,
    )
