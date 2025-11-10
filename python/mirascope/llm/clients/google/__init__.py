"""Google client implementation."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .clients import GoogleClient, clear_cache, client, get_client
    from .model_ids import GoogleModelId
else:
    try:
        from .clients import GoogleClient, clear_cache, client, get_client
        from .model_ids import GoogleModelId
    except ImportError:  # pragma: no cover
        from .._missing_import_stubs import create_client_stub, create_import_error_stub

        GoogleClient = create_client_stub("google", "GoogleClient")
        GoogleModelId = str
        clear_cache = create_import_error_stub("google", "GoogleClient")
        client = create_import_error_stub("google", "GoogleClient")
        get_client = create_import_error_stub("google", "GoogleClient")

__all__ = [
    "GoogleClient",
    "GoogleModelId",
    "clear_cache",
    "client",
    "get_client",
]
