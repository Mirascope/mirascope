"""Tests the `cohere.call` module."""

import sys
from unittest.mock import MagicMock, patch

from mirascope.core.cohere import _utils
from mirascope.core.cohere.call_response import CohereCallResponse
from mirascope.core.cohere.call_response_chunk import CohereCallResponseChunk
from mirascope.core.cohere.stream import CohereStream
from mirascope.core.cohere.tool import CohereTool


def test_cohere_call() -> None:
    """Tests the `cohere_call` decorator."""

    if "mirascope.core.cohere._call" in sys.modules:
        del sys.modules["mirascope.core.cohere._call"]

    with patch(
        "mirascope.core.base.call_factory", new_callable=MagicMock
    ) as mock_call_factory:
        import mirascope.core.cohere._call  # noqa: F401

        mock_call_factory.assert_called_once_with(
            TCallResponse=CohereCallResponse,
            TCallResponseChunk=CohereCallResponseChunk,
            TToolType=CohereTool,
            TStream=CohereStream,
            default_call_params={},
            setup_call=_utils.setup_call,
            get_json_output=_utils.get_json_output,
            handle_stream=_utils.handle_stream,
            handle_stream_async=_utils.handle_stream_async,
        )
