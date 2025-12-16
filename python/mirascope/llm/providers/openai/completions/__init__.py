from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base_provider import BaseOpenAICompletionsProvider
    from .provider import OpenAICompletionsProvider
else:
    try:
        from .base_provider import BaseOpenAICompletionsProvider
        from .provider import OpenAICompletionsProvider
    except ImportError:  # pragma: no cover
        from ..._missing_import_stubs import (
            create_provider_stub,
        )

        BaseOpenAICompletionsProvider = create_provider_stub(
            "openai", "BaseOpenAICompletionsProvider"
        )
        OpenAICompletionsProvider = create_provider_stub(
            "openai", "OpenAICompletionsProvider"
        )

__all__ = [
    "BaseOpenAICompletionsProvider",
    "OpenAICompletionsProvider",
]
