"""Provider registry for managing provider instances and scopes."""

from typing import overload

from ..exceptions import NoRegisteredProviderError
from .base import Provider
from .load_provider import load_provider
from .provider_id import ProviderId

# Global registry mapping scopes to providers
# Scopes are matched by prefix (longest match wins)
PROVIDER_REGISTRY: dict[str, Provider] = {}

# Default auto-registration mapping for built-in providers
# These providers will be automatically registered on first use
DEFAULT_AUTO_REGISTER_SCOPES: dict[str, ProviderId] = {
    "anthropic/": "anthropic",
    "google/": "google",
    "mlx-community/": "mlx",
    "ollama/": "ollama",
    "openai/": "openai",
    "together/": "together",
}


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
        provider = load_provider(provider, api_key=api_key, base_url=base_url)

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

    Args:
        model_id: The full model ID (e.g., "anthropic/claude-4-5-sonnet").

    Returns:
        The provider instance registered for this model.

    Raises:
        ValueError: If no provider is registered or available for this model.

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
        ```
    """
    # Try explicit registry first (longest match wins)
    matching_scopes = [
        scope for scope in PROVIDER_REGISTRY if model_id.startswith(scope)
    ]
    if matching_scopes:
        best_scope = max(matching_scopes, key=len)
        return PROVIDER_REGISTRY[best_scope]

    # Fall back to auto-registration
    matching_defaults = [
        scope for scope in DEFAULT_AUTO_REGISTER_SCOPES if model_id.startswith(scope)
    ]
    if matching_defaults:
        best_scope = max(matching_defaults, key=len)
        provider_id = DEFAULT_AUTO_REGISTER_SCOPES[best_scope]
        provider = load_provider(provider_id)
        # Auto-register for future calls
        PROVIDER_REGISTRY[best_scope] = provider
        return provider

    # No provider found
    raise NoRegisteredProviderError(model_id)
