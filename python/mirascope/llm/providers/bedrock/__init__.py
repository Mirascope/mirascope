"""Bedrock provider implementation."""

from .model_id import BedrockModelId
from .provider import BedrockProvider

__all__ = [
    "BedrockModelId",
    "BedrockProvider",
]

try:
    from .anthropic import BedrockAnthropicProvider
except ImportError:  # pragma: no cover
    pass  # pragma: no cover
else:
    __all__.append("BedrockAnthropicProvider")
