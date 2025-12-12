"""Anthropic client implementation."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .model_id import AnthropicModelId
    from .provider import AnthropicProvider
else:
    try:
        from .model_id import AnthropicModelId
        from .provider import AnthropicProvider
    except ImportError:  # pragma: no cover
        from .._missing_import_stubs import (
            create_import_error_stub,
            create_provider_stub,
        )

        AnthropicProvider = create_provider_stub("anthropic", "AnthropicProvider")
        AnthropicModelId = str

__all__ = [
    "AnthropicModelId",
    "AnthropicProvider",
]
