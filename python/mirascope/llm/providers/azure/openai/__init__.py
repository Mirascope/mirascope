"""Azure OpenAI provider implementation."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .provider import AzureOpenAIProvider, AzureRoutedOpenAIProvider
else:
    try:
        from .provider import AzureOpenAIProvider, AzureRoutedOpenAIProvider
    except ImportError:  # pragma: no cover
        from ..._missing_import_stubs import (
            create_provider_stub,
        )

        AzureOpenAIProvider = create_provider_stub("openai", "AzureOpenAIProvider")
        AzureRoutedOpenAIProvider = create_provider_stub(
            "openai", "AzureRoutedOpenAIProvider"
        )

__all__ = [
    "AzureOpenAIProvider",
    "AzureRoutedOpenAIProvider",
]
