"""Identifiers for all registered providers."""

from typing import Literal, TypeAlias, get_args

KnownProviderId: TypeAlias = Literal[
    "anthropic",  # Anthropic provider via AnthropicProvider
    "google",  # Google provider via GoogleProvider
    "openai",  # OpenAI provider via OpenAIProvider
    "mlx",  # Local inference powered by `mlx-lm`, via MLXProvider
    "together",  # Together provider via TogetherProvider
]
KNOWN_PROVIDER_IDS = get_args(KnownProviderId)

ProviderId = KnownProviderId | str
