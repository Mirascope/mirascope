from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .clients import OpenAICompletionsClient, client
else:
    try:
        from .clients import OpenAICompletionsClient, client
    except ImportError:  # pragma: no cover
        from ..._missing_import_stubs import (
            create_client_stub,
            create_import_error_stub,
        )

        OpenAICompletionsClient = create_client_stub(
            "openai", "OpenAICompletionsClient"
        )
        client = create_import_error_stub("openai", "OpenAICompletionsClient")

__all__ = [
    "OpenAICompletionsClient",
    "client",
]
