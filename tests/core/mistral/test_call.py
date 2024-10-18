"""Tests the `mistral.call` module."""

import sys
from unittest.mock import MagicMock, patch

from mirascope.core.mistral import _utils
from mirascope.core.mistral.call_response import MistralCallResponse
from mirascope.core.mistral.call_response_chunk import MistralCallResponseChunk
from mirascope.core.mistral.stream import MistralStream
from mirascope.core.mistral.tool import MistralTool


def test_mistral_call() -> None:
    """Tests the `mistral_call` decorator."""

    if "mirascope.core.mistral._call" in sys.modules:
        del sys.modules["mirascope.core.mistral._call"]

    with patch(
        "mirascope.core.base.call_factory", new_callable=MagicMock
    ) as mock_call_factory:
        import mirascope.core.mistral._call  # noqa: F401

        mock_call_factory.assert_called_once_with(
            TCallResponse=MistralCallResponse,
            TCallResponseChunk=MistralCallResponseChunk,
            TToolType=MistralTool,
            TStream=MistralStream,
            default_call_params={},
            setup_call=_utils.setup_call,
            get_json_output=_utils.get_json_output,
            handle_stream=_utils.handle_stream,
            handle_stream_async=_utils.handle_stream_async,
        )
