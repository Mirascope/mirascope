"""Ollama provider implementation."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .provider import OllamaProvider
else:
    try:
        from .provider import OllamaProvider
    except ImportError:  # pragma: no cover
        from .._missing_import_stubs import (
            create_provider_stub,
        )

        OllamaProvider = create_provider_stub("openai", "OllamaProvider")

__all__ = [
    "OllamaProvider",
]
