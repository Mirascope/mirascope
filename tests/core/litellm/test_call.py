"""Tests the `litellm.call` module."""

import sys
from unittest.mock import MagicMock, patch

from mirascope.core.litellm._utils import setup_call
from mirascope.core.openai import _utils
from mirascope.core.openai.call_params import OpenAICallParams
from mirascope.core.openai.call_response import OpenAICallResponse
from mirascope.core.openai.call_response_chunk import OpenAICallResponseChunk
from mirascope.core.openai.dynamic_config import OpenAIDynamicConfig
from mirascope.core.openai.stream import OpenAIStream
from mirascope.core.openai.tool import OpenAITool


def test_litellm_call() -> None:
    """Tests the `litellm_call` decorator."""

    if "mirascope.core.litellm._call" in sys.modules:
        del sys.modules["mirascope.core.litellm._call"]

    with patch(
        "mirascope.core.base.call_factory", new_callable=MagicMock
    ) as mock_call_factory:
        import mirascope.core.litellm._call  # noqa: F401

        mock_call_factory.assert_called_once_with(
            TCallResponse=OpenAICallResponse,
            TCallResponseChunk=OpenAICallResponseChunk,
            TDynamicConfig=OpenAIDynamicConfig,
            TToolType=OpenAITool,
            TStream=OpenAIStream,
            TCallParams=OpenAICallParams,
            default_call_params={},
            setup_call=setup_call,
            get_json_output=_utils.get_json_output,
            handle_stream=_utils.handle_stream,
            handle_stream_async=_utils.handle_stream_async,
        )
