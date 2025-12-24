"""Utility functions for Mirascope Router provider."""

import os
from typing import cast

from ..base import Provider
from ..provider_id import ProviderId


def extract_provider_prefix(model_id: str) -> str | None:
    """Extract provider prefix from model ID.

    Args:
        model_id: Model identifier in the format "provider/model-name"
                  e.g., "openai/gpt-4", "anthropic/claude-3", "google/gemini-pro"

    Returns:
        The provider prefix (e.g., "openai", "anthropic", "google") or None if invalid format.
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
        "MIRASCOPE_ROUTER_BASE_URL", "https://mirascope.com/router/v0"
    )


def create_underlying_provider(
    provider_prefix: str, api_key: str, router_base_url: str
) -> Provider:
    """Create and cache an underlying provider instance using provider_singleton.

    This function constructs the appropriate router URL for the provider and
    delegates to provider_singleton for caching and instantiation.

    Args:
        provider_prefix: The provider name (e.g., "openai", "anthropic", "google",
                         "openai:completions", "openai:responses")
        api_key: The API key to use for authentication
        router_base_url: The base router URL (e.g., "http://mirascope.com/router/v0")

    Returns:
        A cached provider instance configured for the Mirascope Router.

    Raises:
        ValueError: If the provider is unsupported.
    """
    # Extract base provider name (handles variants like "openai:completions")
    base_provider = provider_prefix.split(":")[0]

    if base_provider not in ["anthropic", "google", "openai"]:
        raise ValueError(
            f"Unsupported provider: {provider_prefix}. "
            f"Mirascope Router currently supports: anthropic, google, openai"
        )

    base_url = f"{router_base_url}/{base_provider}"
    if base_provider == "openai":  # OpenAI expects /v1, which their SDK doesn't add
        base_url = f"{base_url}/v1"

    # Lazy import to avoid circular dependencies
    from ..provider_registry import provider_singleton

    # Use provider_singleton which provides caching
    return provider_singleton(
        cast(ProviderId, provider_prefix),
        api_key=api_key,
        base_url=base_url,
    )
