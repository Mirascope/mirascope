from typing import Any

from ..providers import ProviderId
from .anthropic import (
    client as anthropic_client,
)
from .base import BaseClient
from .google import (
    client as google_client,
)
from .mlx import (
    client as mlx_client,
)
from .openai import (
    client as openai_client,
)


def client(
    provider: ProviderId, *, api_key: str | None = None, base_url: str | None = None
) -> BaseClient[Any]:
    """Create a cached client instance for the specified provider.

    Args:
        provider: The provider name ("openai", "anthropic", or "google").
        api_key: API key for authentication. If None, uses provider-specific env var.
        base_url: Base URL for the API. If None, uses provider-specific env var.

    Returns:
        A cached client instance for the specified provider with the given parameters.

    Raises:
        ValueError: If the provider is not supported.
    """
    match provider:
        case "anthropic":
            return anthropic_client(api_key=api_key, base_url=base_url)
        case "google":
            return google_client(api_key=api_key, base_url=base_url)
        case "openai":
            return openai_client(api_key=api_key, base_url=base_url)
        case "mlx":  # pragma: no cover (MLX is only available on macOS)
            return mlx_client()
        case _:  # pragma: no cover
            raise ValueError(f"Unknown provider: {provider}")
