"""Interfaces for LLM providers."""

from ..._stubs import stub_module_if_missing

# Stub modules for missing optional dependencies BEFORE importing
# This must happen before any imports from these modules
# Note: We only stub top-level provider modules, not their submodules.
# The _StubModule will automatically handle nested attribute access.
stub_module_if_missing("mirascope.llm.providers.anthropic", "anthropic")
stub_module_if_missing("mirascope.llm.providers.api_route", "openai")
stub_module_if_missing("mirascope.llm.providers.atlascloud", "openai")
stub_module_if_missing("mirascope.llm.providers.cheaperinference", "openai")
stub_module_if_missing("mirascope.llm.providers.google", "google")
stub_module_if_missing("mirascope.llm.providers.llmbuzz", "openai")
stub_module_if_missing("mirascope.llm.providers.mlx", "mlx")
stub_module_if_missing("mirascope.llm.providers.minimax", "openai")
stub_module_if_missing("mirascope.llm.providers.openai", "openai")
stub_module_if_missing("mirascope.llm.providers.openrouter", "openai")
stub_module_if_missing("mirascope.llm.providers.requesty", "openai")
stub_module_if_missing("mirascope.llm.providers.together", "openai")
stub_module_if_missing("mirascope.llm.providers.ollama", "openai")
stub_module_if_missing("mirascope.llm.providers.xai", "openai")

# Now imports work regardless of which packages are installed
# ruff: noqa: E402
from .anthropic import (
    AnthropicModelId,
    AnthropicProvider,
)
from .api_route import APIRouteProvider
from .atlascloud import AtlasCloudProvider
from .base import BaseProvider, Provider
from .cheaperinference import CheaperInferenceProvider
from .google import GoogleModelId, GoogleProvider
from .llmbuzz import LLMBuzzProvider
from .minimax import MiniMaxModelId, MiniMaxProvider
from .mirascope import MirascopeProvider
from .mlx import MLXModelId, MLXProvider
from .model_id import ModelId
from .ollama import OllamaProvider
from .openai import (
    OpenAIModelId,
    OpenAIProvider,
)
from .openai.completions import BaseOpenAICompletionsProvider
from .openrouter import OpenRouterProvider
from .provider_id import KNOWN_PROVIDER_IDS, ProviderId
from .provider_registry import (
    get_provider_for_model,
    register_provider,
    reset_provider_registry,
)
from .requesty import RequestyProvider
from .together import TogetherProvider
from .xai import XAIModelId, XAIProvider

__all__ = [
    "KNOWN_PROVIDER_IDS",
    "APIRouteProvider",
    "AnthropicModelId",
    "AnthropicProvider",
    "AtlasCloudProvider",
    "BaseOpenAICompletionsProvider",
    "BaseProvider",
    "CheaperInferenceProvider",
    "GoogleModelId",
    "GoogleProvider",
    "LLMBuzzProvider",
    "MLXModelId",
    "MLXProvider",
    "MiniMaxModelId",
    "MiniMaxProvider",
    "MirascopeProvider",
    "ModelId",
    "OllamaProvider",
    "OpenAIModelId",
    "OpenAIProvider",
    "OpenRouterProvider",
    "Provider",
    "ProviderId",
    "RequestyProvider",
    "TogetherProvider",
    "XAIModelId",
    "XAIProvider",
    "get_provider_for_model",
    "register_provider",
    "reset_provider_registry",
]
