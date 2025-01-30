"""Tests the `anthropic.call` module."""

import sys
from unittest.mock import MagicMock, patch

from mirascope.core.anthropic import _utils
from mirascope.core.anthropic.call_params import AnthropicCallParams
from mirascope.core.anthropic.call_response import AnthropicCallResponse
from mirascope.core.anthropic.call_response_chunk import AnthropicCallResponseChunk
from mirascope.core.anthropic.stream import AnthropicStream
from mirascope.core.anthropic.tool import AnthropicTool


def test_anthropic_call() -> None:
    """Tests the `anthropic_call` decorator."""

    if "mirascope.core.anthropic._call" in sys.modules:
        del sys.modules["mirascope.core.anthropic._call"]

    with patch(
        "mirascope.core.base.call_factory", new_callable=MagicMock
    ) as mock_call_factory:
        import mirascope.core.anthropic._call  # noqa: F401

        mock_call_factory.assert_called_once_with(
            TCallResponse=AnthropicCallResponse,
            TCallResponseChunk=AnthropicCallResponseChunk,
            TStream=AnthropicStream,
            TToolType=AnthropicTool,
            default_call_params=AnthropicCallParams(max_tokens=1024),
            setup_call=_utils.setup_call,
            get_json_output=_utils.get_json_output,
            handle_stream=_utils.handle_stream,
            handle_stream_async=_utils.handle_stream_async,
        )
