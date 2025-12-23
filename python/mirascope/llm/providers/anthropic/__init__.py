"""Anthropic client implementation."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base_beta_provider import BaseAnthropicBetaProvider
    from .base_provider import BaseAnthropicProvider
    from .beta_provider import AnthropicBetaProvider
    from .model_id import AnthropicModelId
    from .provider import AnthropicProvider
else:
    try:
        from .base_beta_provider import BaseAnthropicBetaProvider
        from .base_provider import BaseAnthropicProvider
        from .beta_provider import AnthropicBetaProvider
        from .model_id import AnthropicModelId
        from .provider import AnthropicProvider
    except ImportError:  # pragma: no cover
        from .._missing_import_stubs import (
            create_provider_stub,
        )

        AnthropicBetaProvider = create_provider_stub(
            "anthropic", "AnthropicBetaProvider"
        )
        AnthropicProvider = create_provider_stub("anthropic", "AnthropicProvider")
        BaseAnthropicProvider = create_provider_stub(
            "anthropic", "BaseAnthropicProvider"
        )
        BaseAnthropicBetaProvider = create_provider_stub(
            "anthropic", "BaseAnthropicBetaProvider"
        )
        AnthropicModelId = str

__all__ = [
    "AnthropicBetaProvider",
    "AnthropicModelId",
    "AnthropicProvider",
    "BaseAnthropicBetaProvider",
    "BaseAnthropicProvider",
]
