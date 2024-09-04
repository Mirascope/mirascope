"""Tests the `azureai.call` module."""

import sys
from unittest.mock import MagicMock, patch

from mirascope.core.azureai import _utils
from mirascope.core.azureai.call_params import AzureAICallParams
from mirascope.core.azureai.call_response import AzureAICallResponse
from mirascope.core.azureai.call_response_chunk import AzureAICallResponseChunk
from mirascope.core.azureai.dynamic_config import AzureAIDynamicConfig
from mirascope.core.azureai.stream import AzureAIStream
from mirascope.core.azureai.tool import AzureAITool


def test_azureai_call() -> None:
    """Tests the `azureai_call` decorator."""

    if "mirascope.core.azureai._call" in sys.modules:
        del sys.modules["mirascope.core.azureai._call"]

    with patch(
        "mirascope.core.base.call_factory", new_callable=MagicMock
    ) as mock_call_factory:
        import mirascope.core.azureai._call  # noqa: F401

        mock_call_factory.assert_called_once_with(
            TCallResponse=AzureAICallResponse,
            TCallResponseChunk=AzureAICallResponseChunk,
            TDynamicConfig=AzureAIDynamicConfig,
            TToolType=AzureAITool,
            TStream=AzureAIStream,
            TCallParams=AzureAICallParams,
            default_call_params={},
            setup_call=_utils.setup_call,
            get_json_output=_utils.get_json_output,
            handle_stream=_utils.handle_stream,
            handle_stream_async=_utils.handle_stream_async,
        )
