"""MLX client implementation."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .model_id import MLXModelId
    from .provider import MLXProvider
else:
    try:
        from .model_id import MLXModelId
        from .provider import MLXProvider
    except ImportError:  # pragma: no cover
        from .._missing_import_stubs import (
            create_import_error_stub,
            create_provider_stub,
        )

        MLXProvider = create_provider_stub("mlx", "MLXProvider")
        MLXModelId = str

__all__ = [
    "MLXModelId",
    "MLXProvider",
]
