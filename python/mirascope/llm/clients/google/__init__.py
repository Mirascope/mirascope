"""Google client implementation."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .clients import GoogleClient, client
    from .model_id import GoogleModelId
else:
    try:
        from .clients import GoogleClient, client
        from .model_id import GoogleModelId
    except ImportError:  # pragma: no cover
        from .._missing_import_stubs import create_client_stub, create_import_error_stub

        GoogleClient = create_client_stub("google", "GoogleClient")
        GoogleModelId = str
        client = create_import_error_stub("google", "GoogleClient")

__all__ = ["GoogleClient", "GoogleModelId", "client"]
