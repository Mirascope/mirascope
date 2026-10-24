"""Identifiers for all registered providers."""

from typing import Literal, TypeAlias, get_args

KnownProviderId: TypeAlias = Literal[
    "anthropic",  # Anthropic provider via AnthropicProvider
    "anthropic-beta",  # Anthropic beta provider via AnthropicBetaProvider
    "api-route",  # API Route provider via APIRouteProvider
    "atlascloud",  # Atlas Cloud provider via AtlasCloudProvider
    "cheaperinference",  # Cheaper Inference provider via CheaperInferenceProvider
    "google",  # Google provider via GoogleProvider
    "minimax",  # MiniMax provider via MiniMaxProvider
    "mirascope",  # Mirascope Router provider via MirascopeProvider
    "mlx",  # Local inference powered by `mlx-lm`, via MLXProvider
    "ollama",  # Ollama provider via OllamaProvider
    "openai",  # OpenAI provider via OpenAIProvider (prefers Responses routing when available)
    "openrouter",  # OpenRouter provider via OpenRouterProvider
    "opper",  # Opper provider via OpperProvider
    "requesty",  # Requesty provider via RequestyProvider
    "together",  # Together AI provider via TogetherProvider
    "xai",  # xAI provider for Grok models via XAIProvider (Responses API)
]
KNOWN_PROVIDER_IDS = get_args(KnownProviderId)

ProviderId = KnownProviderId | str

OpenAICompletionsCompatibleProviderId: TypeAlias = Literal[
    "api-route",  # API Route (OpenAI-compatible)
    "atlascloud",  # Atlas Cloud (OpenAI-compatible)
    "cheaperinference",  # Cheaper Inference (OpenAI-compatible)
    "minimax",  # MiniMax (OpenAI-compatible)
    "ollama",  # Ollama (OpenAI-compatible)
    "openai",  # OpenAI via OpenAIProvider (routes to completions)
    "openai:completions",  # OpenAI Completions API directly
    "openrouter",  # OpenRouter (OpenAI-compatible)
    "opper",  # Opper (OpenAI-compatible)
    "requesty",  # Requesty (OpenAI-compatible)
    "together",  # Together AI (OpenAI-compatible)
]
