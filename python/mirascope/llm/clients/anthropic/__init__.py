"""Anthropic client implementation."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base_client import BaseAnthropicClient
    from .clients import AnthropicClient, clear_cache, client, get_client
    from .model_ids import AnthropicModelId
else:
    try:
        from .base_client import BaseAnthropicClient
        from .clients import AnthropicClient, clear_cache, client, get_client
        from .model_ids import AnthropicModelId
    except ImportError:  # pragma: no cover
        from .._missing_import_stubs import create_client_stub, create_import_error_stub

        AnthropicClient = create_client_stub("anthropic", "AnthropicClient")
        AnthropicModelId = str
        BaseAnthropicClient = create_client_stub("anthropic", "BaseAnthropicClient")
        clear_cache = create_import_error_stub("anthropic", "AnthropicClient")
        client = create_import_error_stub("anthropic", "AnthropicClient")
        get_client = create_import_error_stub("anthropic", "AnthropicClient")

__all__ = [
    "AnthropicClient",
    "AnthropicModelId",
    "BaseAnthropicClient",
    "clear_cache",
    "client",
    "get_client",
]
