from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .provider import OpenAIResponsesProvider
else:
    try:
        from .provider import OpenAIResponsesProvider
    except ImportError:  # pragma: no cover
        from ..._missing_import_stubs import (
            create_import_error_stub,
            create_provider_stub,
        )

        OpenAIResponsesProvider = create_provider_stub(
            "openai", "OpenAIResponsesProvider"
        )


__all__ = [
    "OpenAIResponsesProvider",
]
