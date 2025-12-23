"""Azure Anthropic provider implementation."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .beta_provider import (
        AzureAnthropicBetaProvider,
        AzureRoutedAnthropicBetaProvider,
    )
    from .provider import AzureAnthropicProvider, AzureRoutedAnthropicProvider
else:
    try:
        from .beta_provider import (
            AzureAnthropicBetaProvider,
            AzureRoutedAnthropicBetaProvider,
        )
        from .provider import AzureAnthropicProvider, AzureRoutedAnthropicProvider
    except ImportError:  # pragma: no cover
        from ..._missing_import_stubs import create_provider_stub

        AzureAnthropicProvider = create_provider_stub(
            "anthropic", "AzureAnthropicProvider"
        )
        AzureRoutedAnthropicProvider = create_provider_stub(
            "anthropic", "AzureRoutedAnthropicProvider"
        )
        AzureAnthropicBetaProvider = create_provider_stub(
            "anthropic", "AzureAnthropicBetaProvider"
        )
        AzureRoutedAnthropicBetaProvider = create_provider_stub(
            "anthropic", "AzureRoutedAnthropicBetaProvider"
        )

__all__ = [
    "AzureAnthropicBetaProvider",
    "AzureAnthropicProvider",
    "AzureRoutedAnthropicBetaProvider",
    "AzureRoutedAnthropicProvider",
]
