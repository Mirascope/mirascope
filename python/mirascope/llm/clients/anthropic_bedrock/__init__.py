"""Anthropic Bedrock client implementations."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..anthropic import BaseAnthropicClient
    from .clients import AnthropicBedrockClient, clear_cache, client, get_client
    from .model_ids import AnthropicBedrockModelId
else:
    try:
        from ..anthropic import BaseAnthropicClient
        from .clients import AnthropicBedrockClient, clear_cache, client, get_client
        from .model_ids import AnthropicBedrockModelId
    except ImportError:  # pragma: no cover
        from .._missing_import_stubs import create_client_stub, create_import_error_stub

        AnthropicBedrockClient = create_client_stub(
            "anthropic", "AnthropicBedrockClient"
        )
        AnthropicBedrockModelId = str
        BaseAnthropicClient = create_client_stub("anthropic", "BaseAnthropicClient")
        clear_cache = create_import_error_stub("anthropic", "AnthropicBedrockClient")
        client = create_import_error_stub("anthropic", "AnthropicBedrockClient")
        get_client = create_import_error_stub("anthropic", "AnthropicBedrockClient")

__all__ = [
    "AnthropicBedrockClient",
    "AnthropicBedrockModelId",
    "BaseAnthropicClient",
    "clear_cache",
    "client",
    "get_client",
]
