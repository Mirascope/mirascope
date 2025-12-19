"""Azure provider implementation."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
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

__all__ = [
    "AzureModelId",
    "AzureOpenAIProvider",
    "AzureProvider",
]
