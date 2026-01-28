"""Azure provider implementation."""

from ...._stubs import stub_module_if_missing

# Stub Azure submodules before import so missing optional deps fail on use.
stub_module_if_missing("mirascope.llm.providers.azure.openai", "openai")
stub_module_if_missing("mirascope.llm.providers.azure.anthropic", "anthropic")

# ruff: noqa: E402
from .anthropic import AzureAnthropicProvider
from .model_id import AzureModelId
from .openai import AzureOpenAIProvider
from .provider import AzureProvider

__all__ = [
    "AzureAnthropicProvider",
    "AzureModelId",
    "AzureOpenAIProvider",
    "AzureProvider",
]
