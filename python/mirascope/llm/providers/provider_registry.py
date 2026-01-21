"""Provider registry for managing provider instances and scopes."""

import os
from collections.abc import Sequence
from dataclasses import dataclass
from functools import lru_cache
from typing import overload

from ..exceptions import MissingAPIKeyError, NoRegisteredProviderError
from .anthropic import AnthropicProvider
from .base import Provider
from .google import GoogleProvider
from .mirascope import MirascopeProvider
from .mlx import MLXProvider
from .ollama import OllamaProvider
from .openai import OpenAIProvider
from .openai.completions.provider import OpenAICompletionsProvider
from .openai.responses.provider import OpenAIResponsesProvider
from .provider_id import ProviderId
from .together import TogetherProvider

# Global registry mapping scopes to providers
# Scopes are matched by prefix (longest match wins)
PROVIDER_REGISTRY: dict[str, Provider] = {}


def reset_provider_registry() -> None:
    """Resets the provider registry, clearing all registered providers."""
    PROVIDER_REGISTRY.clear()
    provider_singleton.cache_clear()


@dataclass(frozen=True)
class ProviderDefault:
    """Configuration for a provider in the auto-registration fallback chain.

    When auto-registering a provider for a scope, the fallback chain is tried
    in order. The first provider whose API key is available will be used.
    """

    provider_id: ProviderId
    """The provider identifier."""

    api_key_env_var: str | None
    """Environment variable for the API key, or None if no key is required."""


# Fallback chain for auto-registration: try providers in order until one has
# its API key available. This enables automatic fallback to Mirascope Router
# when direct provider keys are not set.
DEFAULT_AUTO_REGISTER_SCOPES: dict[str, Sequence[ProviderDefault]] = {
    "anthropic/": [
        ProviderDefault("anthropic", "ANTHROPIC_API_KEY"),
        ProviderDefault("mirascope", "MIRASCOPE_API_KEY"),
    ],
    "google/": [
        ProviderDefault("google", "GOOGLE_API_KEY"),
        ProviderDefault("mirascope", "MIRASCOPE_API_KEY"),
    ],
    "openai/": [
        ProviderDefault("openai", "OPENAI_API_KEY"),
        ProviderDefault("mirascope", "MIRASCOPE_API_KEY"),
    ],
    "together/": [
        ProviderDefault("together", "TOGETHER_API_KEY"),
        # No Mirascope fallback for together
    ],
    "ollama/": [
        ProviderDefault("ollama", None),  # No API key required
    ],
    "mlx-community/": [
        ProviderDefault("mlx", None),  # No API key required
    ],
}


def _has_api_key(default: ProviderDefault) -> bool:
    """Check if the API key for a provider default is available.

    Args:
        default: The provider default configuration to check.

    Returns:
        True if the API key is available or not required, False otherwise.
    """
    if default.api_key_env_var is None:
        return True  # Provider doesn't require API key
    return os.environ.get(default.api_key_env_var) is not None


@lru_cache(maxsize=256)
def provider_singleton(
    provider_id: ProviderId, *, api_key: str | None = None, base_url: str | None = None
) -> Provider:
    """Create a cached provider instance for the specified provider id.

    Args:
        provider_id: The provider name ("openai", "anthropic", or "google").
        api_key: API key for authentication. If None, uses provider-specific env var.
        base_url: Base URL for the API. If None, uses provider-specific env var.

    Returns:
        A cached provider instance for the specified provider with the given parameters.

    Raises:
        ValueError: If the provider_id is not supported.
    """
    match provider_id:
        case "anthropic":
            return AnthropicProvider(api_key=api_key, base_url=base_url)
        case "google":
            return GoogleProvider(api_key=api_key, base_url=base_url)
        case "mirascope":
            return MirascopeProvider(api_key=api_key, base_url=base_url)
        case "mlx":  # pragma: no cover (MLX is only available on macOS)
            return MLXProvider()
        case "ollama":
            return OllamaProvider(api_key=api_key, base_url=base_url)
        case "openai":
            return OpenAIProvider(api_key=api_key, base_url=base_url)
        case "openai:completions":
            return OpenAICompletionsProvider(api_key=api_key, base_url=base_url)
        case "openai:responses":
            return OpenAIResponsesProvider(api_key=api_key, base_url=base_url)
        case "together":
            return TogetherProvider(api_key=api_key, base_url=base_url)
        case _:  # pragma: no cover
            raise ValueError(f"Unknown provider: '{provider_id}'")


@overload
def register_provider(
    provider: Provider,
    scope: str | list[str] | None = None,
) -> Provider:
    """Register a provider instance with scope(s).

    Args:
        provider: Provider instance to register.
        scope: Scope string or list of scopes (e.g., "anthropic/", ["anthropic/", "openai/"]).
            If None, uses the provider's default_scope.
    """
    ...


@overload
def register_provider(
    provider: ProviderId,
    scope: str | list[str] | None = None,
    *,
    api_key: str | None = None,
    base_url: str | None = None,
) -> Provider:
    """Register a provider by ID with scope(s).

    Args:
        provider: Provider ID string (e.g., "anthropic", "openai").
        scope: Scope string or list of scopes (e.g., "anthropic/", ["anthropic/", "openai/"]).
            If None, uses the provider's default_scope.
        api_key: API key for authentication.
        base_url: Base URL for the API.
    """
    ...


def register_provider(
    provider: ProviderId | Provider,
    scope: str | list[str] | None = None,
    *,
    api_key: str | None = None,
    base_url: str | None = None,
) -> Provider:
    """Register a provider with scope(s) in the global registry.

    Scopes use prefix matching on model IDs:
    - "anthropic/" matches "anthropic/*"
    - "anthropic/claude-4-5" matches "anthropic/claude-4-5*"
    - "anthropic/claude-4-5-sonnet" matches exactly "anthropic/claude-4-5-sonnet"

    When multiple scopes match a model_id, the longest match wins.

    Args:
        provider: Either a provider ID string or a provider instance.
        scope: Scope string or list of scopes for prefix matching on model IDs.
            If None, uses the provider's default_scope attribute.
            Can be a single string or a list of strings.
        api_key: API key for authentication (only used if provider is a string).
        base_url: Base URL for the API (only used if provider is a string).

    Example:
        ```python
        # Register with default scope
        llm.register_provider("anthropic", api_key="key")

        # Register for specific models
        llm.register_provider("openai", scope="openai/gpt-4")

        # Register for multiple scopes
        llm.register_provider("aws-bedrock", scope=["anthropic/", "openai/"])

        # Register a custom instance
        custom = llm.providers.AnthropicProvider(api_key="team-key")
        llm.register_provider(custom, scope="anthropic/claude-4-5-sonnet")
        ```
    """

    if isinstance(provider, str):
        provider = provider_singleton(provider, api_key=api_key, base_url=base_url)

    if scope is None:
        scope = provider.default_scope

    scopes = [scope] if isinstance(scope, str) else scope
    for s in scopes:
        PROVIDER_REGISTRY[s] = provider

    return provider


def get_provider_for_model(model_id: str) -> Provider:
    """Get the provider for a model_id based on the registry.

    Uses longest prefix matching to find the most specific provider for the model.
    If no explicit registration is found, checks for auto-registration defaults
    and automatically registers the provider on first use.

    When auto-registering, providers are tried in fallback order. For example,
    if ANTHROPIC_API_KEY is not set but MIRASCOPE_API_KEY is, the Mirascope
    Router will be used as a fallback for anthropic/ models.

    Args:
        model_id: The full model ID (e.g., "anthropic/claude-4-5-sonnet").

    Returns:
        The provider instance registered for this model.

    Raises:
        NoRegisteredProviderError: If no provider scope matches the model_id.
        MissingAPIKeyError: If no provider in the fallback chain has its API key set.

    Example:
        ```python
        # Assuming providers are registered:
        # - "anthropic/" -> AnthropicProvider()
        # - "anthropic/claude-4-5-sonnet" -> CustomProvider()

        provider = get_provider_for_model("anthropic/claude-4-5-sonnet")
        # Returns CustomProvider (longest match)

        provider = get_provider_for_model("anthropic/claude-3-opus")
        # Returns AnthropicProvider (matches "anthropic/" prefix)

        # Auto-registration on first use:
        provider = get_provider_for_model("openai/gpt-4")
        # Automatically loads and registers OpenAIProvider() for "openai/"

        # Fallback to Mirascope Router if direct key missing:
        # (with MIRASCOPE_API_KEY set but not ANTHROPIC_API_KEY)
        provider = get_provider_for_model("anthropic/claude-4-5-sonnet")
        # Returns MirascopeProvider registered for "anthropic/" scope
        ```
    """
    # Try explicit registry first (longest match wins)
    matching_scopes = [
        scope for scope in PROVIDER_REGISTRY if model_id.startswith(scope)
    ]
    if matching_scopes:
        best_scope = max(matching_scopes, key=len)
        return PROVIDER_REGISTRY[best_scope]

    # Fall back to auto-registration with fallback chain
    matching_defaults = [
        scope for scope in DEFAULT_AUTO_REGISTER_SCOPES if model_id.startswith(scope)
    ]
    if matching_defaults:
        best_scope = max(matching_defaults, key=len)
        fallback_chain = DEFAULT_AUTO_REGISTER_SCOPES[best_scope]

        # Try each provider in the fallback chain
        for default in fallback_chain:
            if _has_api_key(default):
                provider = provider_singleton(default.provider_id)
                # Register for just this scope (not all provider's default scopes)
                PROVIDER_REGISTRY[best_scope] = provider
                return provider

        # No provider in chain has API key - raise helpful error
        primary = fallback_chain[0]
        has_mirascope_fallback = any(
            d.provider_id == "mirascope" for d in fallback_chain
        )
        raise MissingAPIKeyError(
            provider_id=primary.provider_id,
            env_var=primary.api_key_env_var or "",
            has_mirascope_fallback=has_mirascope_fallback,
        )

    # No matching scope at all
    raise NoRegisteredProviderError(model_id)
