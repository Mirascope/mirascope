"""Anthropic client implementation."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .beta_provider import AnthropicBetaProvider
    from .model_id import AnthropicModelId
    from .provider import AnthropicProvider
else:
    try:
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
        AnthropicModelId = str

__all__ = [
    "AnthropicBetaProvider",
    "AnthropicModelId",
    "AnthropicProvider",
]
