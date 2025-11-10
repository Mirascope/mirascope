"""Azure OpenAI Completions API client."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .clients import AzureOpenAICompletionsClient, clear_cache, client, get_client
    from .model_ids import AzureOpenAICompletionsModelId
else:
    try:
        from .clients import (
            AzureOpenAICompletionsClient,
            clear_cache,
            client,
            get_client,
        )
        from .model_ids import AzureOpenAICompletionsModelId
    except ImportError:  # pragma: no cover
        from ..._missing_import_stubs import (
            create_client_stub,
            create_import_error_stub,
        )

        AzureOpenAICompletionsClient = create_client_stub(
            "openai", "AzureOpenAICompletionsClient"
        )
        AzureOpenAICompletionsModelId = str
        clear_cache = create_import_error_stub("openai", "AzureOpenAICompletionsClient")
        client = create_import_error_stub("openai", "AzureOpenAICompletionsClient")
        get_client = create_import_error_stub("openai", "AzureOpenAICompletionsClient")

__all__ = [
    "AzureOpenAICompletionsClient",
    "AzureOpenAICompletionsModelId",
    "clear_cache",
    "client",
    "get_client",
]
