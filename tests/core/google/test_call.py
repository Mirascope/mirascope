"""Tests the `gemini.call` module."""

import sys
from unittest.mock import MagicMock, patch

from mirascope.core.gemini import _utils
from mirascope.core.gemini.call_response import GeminiCallResponse
from mirascope.core.gemini.call_response_chunk import GeminiCallResponseChunk
from mirascope.core.gemini.stream import GeminiStream
from mirascope.core.gemini.tool import GeminiTool


def test_gemini_call() -> None:
    """Tests the `gemini_call` decorator."""

    if "mirascope.core.gemini._call" in sys.modules:
        del sys.modules["mirascope.core.gemini._call"]

    with patch(
        "mirascope.core.base.call_factory", new_callable=MagicMock
    ) as mock_call_factory:
        import mirascope.core.gemini._call  # noqa: F401

        mock_call_factory.assert_called_once_with(
            TCallResponse=GeminiCallResponse,
            TCallResponseChunk=GeminiCallResponseChunk,
            TToolType=GeminiTool,
            TStream=GeminiStream,
            default_call_params={},
            setup_call=_utils.setup_call,
            get_json_output=_utils.get_json_output,
            handle_stream=_utils.handle_stream,
            handle_stream_async=_utils.handle_stream_async,
        )
