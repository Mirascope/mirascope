"""Tests the `azure.call` module."""

import sys
from unittest.mock import MagicMock, patch

from mirascope.core.azure import _utils
from mirascope.core.azure.call_response import AzureCallResponse
from mirascope.core.azure.call_response_chunk import AzureCallResponseChunk
from mirascope.core.azure.stream import AzureStream
from mirascope.core.azure.tool import AzureTool


def test_azure_call() -> None:
    """Tests the `azure_call` decorator."""

    if "mirascope.core.azure._call" in sys.modules:
        del sys.modules["mirascope.core.azure._call"]

    with patch(
        "mirascope.core.base.call_factory", new_callable=MagicMock
    ) as mock_call_factory:
        import mirascope.core.azure._call  # noqa: F401

        mock_call_factory.assert_called_once_with(
            TCallResponse=AzureCallResponse,
            TCallResponseChunk=AzureCallResponseChunk,
            TToolType=AzureTool,
            TStream=AzureStream,
            default_call_params={},
            setup_call=_utils.setup_call,
            get_json_output=_utils.get_json_output,
            handle_stream=_utils.handle_stream,
            handle_stream_async=_utils.handle_stream_async,
        )
