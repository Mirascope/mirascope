"""Anthropic Vertex AI client implementations."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..anthropic import BaseAnthropicClient
    from .clients import AnthropicVertexClient, clear_cache, client, get_client
    from .model_ids import AnthropicVertexModelId
else:
    try:
        from ..anthropic import BaseAnthropicClient
        from .clients import AnthropicVertexClient, clear_cache, client, get_client
        from .model_ids import AnthropicVertexModelId
    except ImportError:  # pragma: no cover
        from .._missing_import_stubs import create_client_stub, create_import_error_stub

        AnthropicVertexClient = create_client_stub(
            "anthropic", "AnthropicVertexClient"
        )
        AnthropicVertexModelId = str
        BaseAnthropicClient = create_client_stub("anthropic", "BaseAnthropicClient")
        clear_cache = create_import_error_stub("anthropic", "AnthropicVertexClient")
        client = create_import_error_stub("anthropic", "AnthropicVertexClient")
        get_client = create_import_error_stub("anthropic", "AnthropicVertexClient")

__all__ = [
    "AnthropicVertexClient",
    "AnthropicVertexModelId",
    "BaseAnthropicClient",
    "clear_cache",
    "client",
    "get_client",
]
