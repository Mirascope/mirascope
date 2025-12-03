"""Anthropic client implementation."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .clients import AnthropicClient, client, get_client
    from .model_ids import AnthropicModelId
else:
    try:
        from .clients import AnthropicClient, client, get_client
        from .model_ids import AnthropicModelId
    except ImportError:  # pragma: no cover
        from .._missing_import_stubs import create_client_stub, create_import_error_stub

        AnthropicClient = create_client_stub("anthropic", "AnthropicClient")
        AnthropicModelId = str
        client = create_import_error_stub("anthropic", "AnthropicClient")
        get_client = create_import_error_stub("anthropic", "AnthropicClient")

__all__ = [
    "AnthropicClient",
    "AnthropicModelId",
    "client",
    "get_client",
]
