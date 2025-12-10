"""MLX client implementation."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .clients import MLXClient, client
    from .model_id import MLXModelId
else:
    try:
        from .clients import MLXClient, client
        from .model_id import MLXModelId
    except ImportError:  # pragma: no cover
        from .._missing_import_stubs import create_client_stub, create_import_error_stub

        MLXClient = create_client_stub("mlx", "MLXClient")
        MLXModelId = str
        client = create_import_error_stub("mlx", "MLXClient")

__all__ = [
    "MLXClient",
    "MLXModelId",
    "client",
]
