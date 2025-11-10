"""Azure OpenAI Responses API client."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .clients import AzureOpenAIResponsesClient, clear_cache, client, get_client
    from .model_ids import AzureOpenAIResponsesModelId
else:
    try:
        from .clients import AzureOpenAIResponsesClient, clear_cache, client, get_client
        from .model_ids import AzureOpenAIResponsesModelId
    except ImportError:  # pragma: no cover
        from ..._missing_import_stubs import (
            create_client_stub,
            create_import_error_stub,
        )

        AzureOpenAIResponsesClient = create_client_stub(
            "openai", "AzureOpenAIResponsesClient"
        )
        AzureOpenAIResponsesModelId = str
        clear_cache = create_import_error_stub("openai", "AzureOpenAIResponsesClient")
        client = create_import_error_stub("openai", "AzureOpenAIResponsesClient")
        get_client = create_import_error_stub("openai", "AzureOpenAIResponsesClient")

__all__ = [
    "AzureOpenAIResponsesClient",
    "AzureOpenAIResponsesModelId",
    "clear_cache",
    "client",
    "get_client",
]
