"""The Mirascope Azure Module."""

from ._call import azure_call
from ._call import azure_call as call
from .call_params import AzureCallParams
from .call_response import AzureCallResponse
from .call_response_chunk import AzureCallResponseChunk
from .dynamic_config import AzureDynamicConfig
from .stream import AzureStream
from .tool import AzureTool, AzureToolConfig

__all__ = [
    "call",
    "AzureDynamicConfig",
    "AzureCallParams",
    "AzureCallResponse",
    "AzureCallResponseChunk",
    "AzureStream",
    "AzureTool",
    "AzureToolConfig",
    "azure_call",
]
