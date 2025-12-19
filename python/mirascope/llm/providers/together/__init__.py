"""Together AI provider implementation."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .provider import TogetherProvider
else:
    try:
        from .provider import TogetherProvider
    except ImportError:  # pragma: no cover
        from .._missing_import_stubs import (
            create_provider_stub,
        )

        TogetherProvider = create_provider_stub("openai", "TogetherProvider")

__all__ = [
    "TogetherProvider",
]
