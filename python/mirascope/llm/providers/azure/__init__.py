"""Azure provider implementation."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .anthropic import (
        AzureAnthropicBetaProvider,
        AzureAnthropicProvider,
        AzureRoutedAnthropicBetaProvider,
        AzureRoutedAnthropicProvider,
    )
    from .model_id import AzureModelId
    from .openai import AzureOpenAIProvider
    from .provider import AzureProvider
else:
    try:
        from .model_id import AzureModelId
        from .openai import AzureOpenAIProvider
        from .provider import AzureProvider
    except ImportError:  # pragma: no cover
        from .._missing_import_stubs import (
            create_provider_stub,
        )

        AzureProvider = create_provider_stub("openai", "AzureProvider")
        AzureOpenAIProvider = create_provider_stub("openai", "AzureOpenAIProvider")
        AzureModelId = str

    try:
        from .anthropic import (
            AzureAnthropicBetaProvider,
            AzureAnthropicProvider,
            AzureRoutedAnthropicBetaProvider,
            AzureRoutedAnthropicProvider,
        )
    except ImportError:  # pragma: no cover
        from .._missing_import_stubs import create_provider_stub

        AzureAnthropicProvider = create_provider_stub(
            "anthropic", "AzureAnthropicProvider"
        )
        AzureAnthropicBetaProvider = create_provider_stub(
            "anthropic", "AzureAnthropicBetaProvider"
        )
        AzureRoutedAnthropicProvider = create_provider_stub(
            "anthropic", "AzureRoutedAnthropicProvider"
        )
        AzureRoutedAnthropicBetaProvider = create_provider_stub(
            "anthropic", "AzureRoutedAnthropicBetaProvider"
        )

__all__ = [
    "AzureAnthropicBetaProvider",
    "AzureAnthropicProvider",
    "AzureModelId",
    "AzureOpenAIProvider",
    "AzureProvider",
    "AzureRoutedAnthropicBetaProvider",
    "AzureRoutedAnthropicProvider",
]
