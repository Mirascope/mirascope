"""Interfaces for LLM providers."""

from ..._stubs import stub_module_if_missing

# Stub modules for missing optional dependencies BEFORE importing
# This must happen before any imports from these modules
# Note: We only stub top-level provider modules, not their submodules.
# The _StubModule will automatically handle nested attribute access.
stub_module_if_missing("mirascope.llm.providers.anthropic", "anthropic")
stub_module_if_missing("mirascope.llm.providers.google", "google")
stub_module_if_missing("mirascope.llm.providers.mlx", "mlx")
stub_module_if_missing("mirascope.llm.providers.openai", "openai")
stub_module_if_missing("mirascope.llm.providers.together", "openai")
stub_module_if_missing("mirascope.llm.providers.ollama", "openai")

# Now imports work regardless of which packages are installed
# ruff: noqa: E402
from .anthropic import (
    AnthropicModelId,
    AnthropicProvider,
)
from .base import BaseProvider, Provider
from .google import GoogleModelId, GoogleProvider
from .mirascope import MirascopeProvider
from .mlx import MLXModelId, MLXProvider
from .model_id import ModelId
from .ollama import OllamaProvider
from .openai import (
    OpenAIModelId,
    OpenAIProvider,
)
from .openai.completions import BaseOpenAICompletionsProvider
from .provider_id import KNOWN_PROVIDER_IDS, ProviderId
from .provider_registry import (
    get_provider_for_model,
    register_provider,
    reset_provider_registry,
)
from .together import TogetherProvider

__all__ = [
    "KNOWN_PROVIDER_IDS",
    "AnthropicModelId",
    "AnthropicProvider",
    "BaseOpenAICompletionsProvider",
    "BaseProvider",
    "GoogleModelId",
    "GoogleProvider",
    "MLXModelId",
    "MLXProvider",
    "MirascopeProvider",
    "ModelId",
    "OllamaProvider",
    "OpenAIModelId",
    "OpenAIProvider",
    "Provider",
    "ProviderId",
    "TogetherProvider",
    "get_provider_for_model",
    "register_provider",
    "reset_provider_registry",
]
