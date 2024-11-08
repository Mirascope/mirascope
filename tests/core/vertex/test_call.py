"""Tests the `vertex.call` module."""

import sys
from unittest.mock import MagicMock, patch

from mirascope.core.vertex import _utils
from mirascope.core.vertex.call_response import VertexCallResponse
from mirascope.core.vertex.call_response_chunk import VertexCallResponseChunk
from mirascope.core.vertex.stream import VertexStream
from mirascope.core.vertex.tool import VertexTool


def test_vertex_call() -> None:
    """Tests the `vertex_call` decorator."""

    if "mirascope.core.vertex._call" in sys.modules:
        del sys.modules["mirascope.core.vertex._call"]

    with patch(
        "mirascope.core.base.call_factory", new_callable=MagicMock
    ) as mock_call_factory:
        import mirascope.core.vertex._call  # noqa: F401

        mock_call_factory.assert_called_once_with(
            TCallResponse=VertexCallResponse,
            TCallResponseChunk=VertexCallResponseChunk,
            TToolType=VertexTool,
            TStream=VertexStream,
            default_call_params={},
            setup_call=_utils.setup_call,
            get_json_output=_utils.get_json_output,
            handle_stream=_utils.handle_stream,
            handle_stream_async=_utils.handle_stream_async,
        )
