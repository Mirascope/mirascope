"""Tests the `bedrock.call` module."""

import sys
from unittest.mock import MagicMock, patch

from mirascope.core.bedrock import _utils
from mirascope.core.bedrock.call_params import BedrockCallParams
from mirascope.core.bedrock.call_response import BedrockCallResponse
from mirascope.core.bedrock.call_response_chunk import BedrockCallResponseChunk
from mirascope.core.bedrock.stream import BedrockStream
from mirascope.core.bedrock.tool import BedrockTool


def test_bedrock_call() -> None:
    """Tests the `bedrock_call` decorator."""

    if "mirascope.core.bedrock._call" in sys.modules:
        del sys.modules["mirascope.core.bedrock._call"]

    with patch(
        "mirascope.core.base.call_factory", new_callable=MagicMock
    ) as mock_call_factory:
        import mirascope.core.bedrock._call  # noqa: F401

        mock_call_factory.assert_called_once_with(
            TCallResponse=BedrockCallResponse,
            TCallResponseChunk=BedrockCallResponseChunk,
            TStream=BedrockStream,
            TToolType=BedrockTool,
            default_call_params=BedrockCallParams(),
            setup_call=_utils.setup_call,
            get_json_output=_utils.get_json_output,
            handle_stream=_utils.handle_stream,
            handle_stream_async=_utils.handle_stream_async,
        )
