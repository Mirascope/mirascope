from functools import lru_cache

from .anthropic import AnthropicProvider
from .base import Provider
from .google import GoogleProvider
from .mlx import MLXProvider
from .ollama import OllamaProvider
from .openai import OpenAIProvider
from .openai.completions.provider import OpenAICompletionsProvider
from .openai.responses.provider import OpenAIResponsesProvider
from .provider_id import ProviderId
from .together import TogetherProvider


@lru_cache(maxsize=256)
def load_provider(
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


load = load_provider
"""Convenient alias as `llm.providers.load`"""
