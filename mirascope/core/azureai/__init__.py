"""The Mirascope AzureAI Module."""

from ._call import azureai_call
from ._call import azureai_call as call
from .call_params import AzureAICallParams
from .call_response import AzureAICallResponse
from .call_response_chunk import AzureAICallResponseChunk
from .dynamic_config import AzureAIDynamicConfig
from .stream import AzureAIStream
from .tool import AzureAITool, AzureAIToolConfig

__all__ = [
    "call",
    "AzureAIDynamicConfig",
    "AzureAICallParams",
    "AzureAICallResponse",
    "AzureAICallResponseChunk",
    "AzureAIStream",
    "AzureAITool",
    "AzureAIToolConfig",
    "azureai_call",
]
