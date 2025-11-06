from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .clients import OpenAICompletionsClient, client, get_client
    from .model_ids import OpenAICompletionsModelId
else:
    try:
        from .clients import OpenAICompletionsClient, client, get_client
        from .model_ids import OpenAICompletionsModelId
    except ImportError:  # pragma: no cover
        from ..._missing_import_stubs import (
            create_client_stub,
            create_import_error_stub,
        )

        OpenAICompletionsClient = create_client_stub(
            "openai", "OpenAICompletionsClient"
        )
        OpenAICompletionsModelId = str
        client = create_import_error_stub("openai", "OpenAICompletionsClient")
        get_client = create_import_error_stub("openai", "OpenAICompletionsClient")

__all__ = [
    "OpenAICompletionsClient",
    "OpenAICompletionsModelId",
    "client",
    "get_client",
]
