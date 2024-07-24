from unittest.mock import MagicMock

from mirascope.core.base._stream import BaseStream
from mirascope.core.base.call_response import BaseCallResponse
from mirascope.core.base.metadata import Metadata
from mirascope.integrations.langfuse import _utils


def test_get_call_response_observation():
    mock_result = MagicMock(spec=BaseCallResponse)
    mock_result.model = "test_model"
    mock_result.prompt_template = "test_prompt_template"
    mock_result.response = "test_response"
    mock_result.message_param = {"role": "assistant", "content": "test_content"}
    mock_fn = MagicMock(__name__="mock_fn")
    mock_fn.__annotations__ = {"metadata": Metadata(tags={"tag1"})}
    call_response_observation = _utils.get_call_response_observation(
        mock_result, mock_fn
    )
    assert call_response_observation["name"] == "mock_fn with test_model"
    assert call_response_observation["input"] == "test_prompt_template"
    assert call_response_observation["metadata"] == "test_response"
    assert call_response_observation["tags"] == {"tag1"}
    assert call_response_observation["model"] == "test_model"
    assert call_response_observation["output"] == "test_content"


def test_get_stream_observation():
    mock_stream = MagicMock(spec=BaseStream)
    mock_stream.model = "test_model"
    mock_stream.prompt_template = "test_prompt_template"
    mock_stream.message_param = {"role": "assistant", "content": "test_content"}
    mock_fn = MagicMock(__name__="mock_fn")
    mock_fn.__annotations__ = {"metadata": Metadata(tags={"tag1"})}
    stream_observation = _utils.get_stream_observation(mock_stream, mock_fn)
    assert stream_observation["name"] == "mock_fn with test_model"
    assert stream_observation["input"] == "test_prompt_template"
    assert stream_observation["tags"] == {"tag1"}
    assert stream_observation["model"] == "test_model"
    assert stream_observation["output"] == "test_content"
