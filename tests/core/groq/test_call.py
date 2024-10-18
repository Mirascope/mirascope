"""Tests the `groq.call` module."""

import sys
from unittest.mock import MagicMock, patch

from mirascope.core.groq import _utils
from mirascope.core.groq.call_response import GroqCallResponse
from mirascope.core.groq.call_response_chunk import GroqCallResponseChunk
from mirascope.core.groq.stream import GroqStream
from mirascope.core.groq.tool import GroqTool


def test_groq_call() -> None:
    """Tests the `groq_call` decorator."""

    if "mirascope.core.groq._call" in sys.modules:
        del sys.modules["mirascope.core.groq._call"]

    with patch(
        "mirascope.core.base.call_factory", new_callable=MagicMock
    ) as mock_call_factory:
        import mirascope.core.groq._call  # noqa: F401

        mock_call_factory.assert_called_once_with(
            TCallResponse=GroqCallResponse,
            TCallResponseChunk=GroqCallResponseChunk,
            TToolType=GroqTool,
            TStream=GroqStream,
            default_call_params={},
            setup_call=_utils.setup_call,
            get_json_output=_utils.get_json_output,
            handle_stream=_utils.handle_stream,
            handle_stream_async=_utils.handle_stream_async,
        )
