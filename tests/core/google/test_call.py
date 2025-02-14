"""Tests the `google.call` module."""

import sys
from unittest.mock import MagicMock, patch

from mirascope.core.google import _utils
from mirascope.core.google.call_response import GoogleCallResponse
from mirascope.core.google.call_response_chunk import GoogleCallResponseChunk
from mirascope.core.google.stream import GoogleStream
from mirascope.core.google.tool import GoogleTool


def test_google_call() -> None:
    """Tests the `google_call` decorator."""

    if "mirascope.core.google._call" in sys.modules:
        del sys.modules["mirascope.core.google._call"]

    with patch(
        "mirascope.core.base.call_factory", new_callable=MagicMock
    ) as mock_call_factory:
        import mirascope.core.google._call  # noqa: F401

        mock_call_factory.assert_called_once_with(
            TCallResponse=GoogleCallResponse,
            TCallResponseChunk=GoogleCallResponseChunk,
            TToolType=GoogleTool,
            TStream=GoogleStream,
            default_call_params={},
            setup_call=_utils.setup_call,
            get_json_output=_utils.get_json_output,
            handle_stream=_utils.handle_stream,
            handle_stream_async=_utils.handle_stream_async,
        )
