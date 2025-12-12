"""Identifiers for all registered providers."""

from typing import Literal, TypeAlias, get_args

ProviderId: TypeAlias = Literal[
    "anthropic",  # Anthropic provider via AnthropicClient
    "google",  # Google provider via GoogleClient
    "openai",  # OpenAI provider via OpenAIClient
    "mlx",  # Local inference powered by `mlx-lm`, via MLXClient
]
KNOWN_PROVIDER_IDS = get_args(ProviderId)
