"""Identifiers for all registered providers."""

from typing import Literal, TypeAlias, get_args

KnownProviderId: TypeAlias = Literal[
    "anthropic",  # Anthropic provider via AnthropicProvider
    "anthropic-beta",  # Anthropic beta provider via AnthropicBetaProvider
    "google",  # Google provider via GoogleProvider
    "mlx",  # Local inference powered by `mlx-lm`, via MLXProvider
    "ollama",  # Ollama provider via OllamaProvider
    "openai",  # OpenAI provider via OpenAIProvider (prefers Responses routing when available)
    "together",  # Together AI provider via TogetherProvider
]
KNOWN_PROVIDER_IDS = get_args(KnownProviderId)

ProviderId = KnownProviderId | str

OpenAICompletionsCompatibleProviderId: TypeAlias = Literal[
    "ollama",  # Ollama (OpenAI-compatible)
    "openai",  # OpenAI via OpenAIProvider (routes to completions)
    "openai:completions",  # OpenAI Completions API directly
    "together",  # Together AI (OpenAI-compatible)
]
