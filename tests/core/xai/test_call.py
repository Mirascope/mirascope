"""Tests the `xai.call` module."""

import sys
from unittest.mock import MagicMock, patch

from mirascope.core.openai import _utils
from mirascope.core.xai._utils import setup_call
from mirascope.core.xai.call_response import XAICallResponse
from mirascope.core.xai.call_response_chunk import XAICallResponseChunk
from mirascope.core.xai.stream import XAIStream
from mirascope.core.xai.tool import XAITool


def test_xai_call() -> None:
    """Tests the `xai_call` decorator."""

    if "mirascope.core.xai._call" in sys.modules:
        del sys.modules["mirascope.core.xai._call"]

    with patch(
        "mirascope.core.base.call_factory", new_callable=MagicMock
    ) as mock_call_factory:
        import mirascope.core.xai._call  # noqa: F401

        mock_call_factory.assert_called_once_with(
            TCallResponse=XAICallResponse,
            TCallResponseChunk=XAICallResponseChunk,
            TToolType=XAITool,
            TStream=XAIStream,
            default_call_params={},
            setup_call=setup_call,
            get_json_output=_utils.get_json_output,
            handle_stream=_utils.handle_stream,
            handle_stream_async=_utils.handle_stream_async,
        )
