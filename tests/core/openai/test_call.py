"""Tests the `openai.call` module."""

import sys
from unittest.mock import MagicMock, patch

from mirascope.core.openai import _utils
from mirascope.core.openai.call_response import OpenAICallResponse
from mirascope.core.openai.call_response_chunk import OpenAICallResponseChunk
from mirascope.core.openai.stream import OpenAIStream
from mirascope.core.openai.tool import OpenAITool


def test_openai_call() -> None:
    """Tests the `openai_call` decorator."""

    if "mirascope.core.openai._call" in sys.modules:
        del sys.modules["mirascope.core.openai._call"]

    with patch(
        "mirascope.core.base.call_factory", new_callable=MagicMock
    ) as mock_call_factory:
        import mirascope.core.openai._call  # noqa: F401

        mock_call_factory.assert_called_once_with(
            TCallResponse=OpenAICallResponse,
            TCallResponseChunk=OpenAICallResponseChunk,
            TToolType=OpenAITool,
            TStream=OpenAIStream,
            default_call_params={},
            setup_call=_utils.setup_call,
            get_json_output=_utils.get_json_output,
            handle_stream=_utils.handle_stream,
            handle_stream_async=_utils.handle_stream_async,
        )
