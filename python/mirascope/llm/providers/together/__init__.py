"""Together AI provider implementation."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .model_id import TogetherModelId
    from .provider import TogetherProvider
else:
    try:
        from .model_id import TogetherModelId
        from .provider import TogetherProvider
    except ImportError:  # pragma: no cover
        from .._missing_import_stubs import (
            create_import_error_stub,
            create_provider_stub,
        )

        TogetherProvider = create_provider_stub("together", "TogetherProvider")
        TogetherModelId = str

__all__ = [
    "TogetherModelId",
    "TogetherProvider",
]
