from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .clients import OpenAIResponsesClient, client
    from .model_ids import OpenAIResponsesModelId
else:
    try:
        from .clients import OpenAIResponsesClient, client
        from .model_ids import OpenAIResponsesModelId
    except ImportError:  # pragma: no cover
        from ..._missing_import_stubs import (
            create_client_stub,
            create_import_error_stub,
        )

        OpenAIResponsesClient = create_client_stub("openai", "OpenAIResponsesClient")
        OpenAIResponsesModelId = str
        client = create_import_error_stub("openai", "OpenAIResponsesClient")

__all__ = [
    "OpenAIResponsesClient",
    "OpenAIResponsesModelId",
    "client",
]
