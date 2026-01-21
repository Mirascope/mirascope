"""Azure provider implementation."""

from .model_id import AzureModelId
from .provider import AzureProvider

__all__ = [
    "AzureModelId",
    "AzureProvider",
]

try:
    from .openai import AzureOpenAIProvider
except ImportError:
    pass
else:
    __all__.append("AzureOpenAIProvider")

try:
    from .anthropic import AzureAnthropicProvider
except ImportError:
    pass
else:
    __all__.append("AzureAnthropicProvider")
