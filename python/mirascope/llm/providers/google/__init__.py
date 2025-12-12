"""Google client implementation."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .model_id import GoogleModelId
    from .provider import GoogleProvider
else:
    try:
        from .model_id import GoogleModelId
        from .provider import GoogleProvider
    except ImportError:  # pragma: no cover
        from .._missing_import_stubs import (
            create_import_error_stub,
            create_provider_stub,
        )

        GoogleProvider = create_provider_stub("google", "GoogleProvider")
        GoogleModelId = str

__all__ = ["GoogleModelId", "GoogleProvider"]
