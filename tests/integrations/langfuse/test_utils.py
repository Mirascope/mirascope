from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from mirascope.core.base._stream import BaseStream
from mirascope.core.base._structured_stream import BaseStructuredStream
from mirascope.core.base.call_response import BaseCallResponse
from mirascope.core.base.metadata import Metadata
from mirascope.integrations.langfuse import _utils
from mirascope.integrations.langfuse._utils import ModelUsage


def test_get_call_response_observation():
    """Tests the `get_call_response_observation` function."""
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
    """Tests the `get_stream_observation` function."""
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


@patch(
    "mirascope.integrations.langfuse._utils.langfuse_context.update_current_observation",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse._utils.get_call_response_observation",
    new_callable=MagicMock,
)
def test_handle_call_response(
    mock_get_call_response_observation: MagicMock,
    mock_update_current_observation: MagicMock,
) -> None:
    """Tests the `handle_call_response` function."""
    mock_fn = MagicMock(__name__="mock_fn")

    result = MagicMock(spec=BaseCallResponse)
    result.input_tokens = 1
    result.output_tokens = 2
    _utils.handle_call_response(result, mock_fn, None)
    mock_get_call_response_observation.assert_called_once_with(result, mock_fn)
    mock_update_current_observation.assert_called_once_with(
        **mock_get_call_response_observation.return_value,
        usage=ModelUsage(
            input=result.input_tokens,
            output=result.output_tokens,
            unit="TOKENS",
        ),
    )


@patch(
    "mirascope.integrations.langfuse._utils.langfuse_context.update_current_observation",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse._utils.get_call_response_observation",
    new_callable=MagicMock,
)
@pytest.mark.asyncio
async def test_handle_call_response_async(
    mock_get_call_response_observation: MagicMock,
    mock_update_current_observation: MagicMock,
) -> None:
    """Tests the `handle_call_response` function."""
    mock_fn = MagicMock(__name__="mock_fn")

    result = MagicMock(spec=BaseCallResponse)
    result.input_tokens = 1
    result.output_tokens = 2
    await _utils.handle_call_response_async(result, mock_fn, None)
    mock_get_call_response_observation.assert_called_once_with(result, mock_fn)
    mock_update_current_observation.assert_called_once_with(
        **mock_get_call_response_observation.return_value,
        usage=ModelUsage(
            input=result.input_tokens,
            output=result.output_tokens,
            unit="TOKENS",
        ),
    )


@patch(
    "mirascope.integrations.langfuse._utils.langfuse_context.update_current_observation",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse._utils.get_stream_observation",
    new_callable=MagicMock,
)
def test_handle_stream(
    mock_get_stream_observation: MagicMock,
    mock_update_current_observation: MagicMock,
) -> None:
    """Tests the `handle_strea` function."""
    mock_fn = MagicMock(__name__="mock_fn")

    result = MagicMock(spec=BaseStream)
    result.input_tokens = 1
    result.output_tokens = 2
    _utils.handle_stream(result, mock_fn, None)
    mock_get_stream_observation.assert_called_once_with(result, mock_fn)
    mock_update_current_observation.assert_called_once_with(
        **mock_get_stream_observation.return_value,
        usage=ModelUsage(
            input=result.input_tokens,
            output=result.output_tokens,
            unit="TOKENS",
        ),
    )


@patch(
    "mirascope.integrations.langfuse._utils.langfuse_context.update_current_observation",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse._utils.get_stream_observation",
    new_callable=MagicMock,
)
@pytest.mark.asyncio
async def test_handle_stream_async(
    mock_get_stream_observation: MagicMock,
    mock_update_current_observation: MagicMock,
) -> None:
    """Tests the `handle_stream_async` function."""
    mock_fn = MagicMock(__name__="mock_fn")

    result = MagicMock(spec=BaseStream)
    result.input_tokens = 1
    result.output_tokens = 2
    await _utils.handle_stream_async(result, mock_fn, None)
    mock_get_stream_observation.assert_called_once_with(result, mock_fn)
    mock_update_current_observation.assert_called_once_with(
        **mock_get_stream_observation.return_value,
        usage=ModelUsage(
            input=result.input_tokens,
            output=result.output_tokens,
            unit="TOKENS",
        ),
    )


@patch(
    "mirascope.integrations.langfuse._utils.langfuse_context.update_current_observation",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse._utils.get_call_response_observation",
    new_callable=MagicMock,
)
def test_handle_base_model(
    mock_get_call_response_observation: MagicMock,
    mock_update_current_observation: MagicMock,
) -> None:
    """Tests the `handle_base_model` function."""
    mock_fn = MagicMock(__name__="mock_fn")
    result = MagicMock(spec=BaseModel)
    result.input_tokens = 1
    result.output_tokens = 2
    response = MagicMock(spec=BaseCallResponse)
    result._response = response

    _utils.handle_base_model(result, mock_fn, None)
    mock_get_call_response_observation.assert_called_once_with(response, mock_fn)
    mock_update_current_observation.assert_called_once_with(
        **mock_get_call_response_observation.return_value,
        usage=ModelUsage(
            input=response.input_tokens,
            output=response.output_tokens,
            unit="TOKENS",
        ),
        output=result,
    )


@patch(
    "mirascope.integrations.langfuse._utils.langfuse_context.update_current_observation",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse._utils.get_stream_observation",
    new_callable=MagicMock,
)
def test_handle_structured_stream(
    mock_get_stream_observation: MagicMock,
    mock_update_current_observation: MagicMock,
) -> None:
    """Tests the `handle_structured_stream` function."""
    mock_fn = MagicMock(__name__="mock_fn")
    result = MagicMock(spec=BaseStructuredStream)
    result.input_tokens = 1
    result.output_tokens = 2
    result.constructed_response_model = MagicMock()
    stream = MagicMock(spec=BaseStream)
    result.stream = stream

    _utils.handle_structured_stream(result, mock_fn, None)
    mock_get_stream_observation.assert_called_once_with(stream, mock_fn)
    mock_update_current_observation.assert_called_once_with(
        **mock_get_stream_observation.return_value,
        usage=ModelUsage(
            input=stream.input_tokens,
            output=stream.output_tokens,
            unit="TOKENS",
        ),
        output=result.constructed_response_model,
    )


@patch(
    "mirascope.integrations.langfuse._utils.langfuse_context.update_current_observation",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse._utils.get_call_response_observation",
    new_callable=MagicMock,
)
@pytest.mark.asyncio
async def test_handle_base_model_async(
    mock_get_call_response_observation: MagicMock,
    mock_update_current_observation: MagicMock,
) -> None:
    """Tests the `handle_base_model` function."""
    mock_fn = MagicMock(__name__="mock_fn")
    result = MagicMock(spec=BaseModel)
    result.input_tokens = 1
    result.output_tokens = 2
    response = MagicMock(spec=BaseCallResponse)
    result._response = response

    await _utils.handle_base_model_async(result, mock_fn, None)
    mock_get_call_response_observation.assert_called_once_with(response, mock_fn)
    mock_update_current_observation.assert_called_once_with(
        **mock_get_call_response_observation.return_value,
        usage=ModelUsage(
            input=response.input_tokens,
            output=response.output_tokens,
            unit="TOKENS",
        ),
        output=result,
    )


@patch(
    "mirascope.integrations.langfuse._utils.langfuse_context.update_current_observation",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse._utils.get_stream_observation",
    new_callable=MagicMock,
)
@pytest.mark.asyncio
async def test_handle_structured_stream_async(
    mock_get_stream_observation: MagicMock,
    mock_update_current_observation: MagicMock,
) -> None:
    """Tests the `handle_structured_stream_async` function."""
    mock_fn = MagicMock(__name__="mock_fn")
    result = MagicMock(spec=BaseStructuredStream)
    result.input_tokens = 1
    result.output_tokens = 2
    result.constructed_response_model = MagicMock()
    stream = MagicMock(spec=BaseStream)
    result.stream = stream

    await _utils.handle_structured_stream_async(result, mock_fn, None)
    mock_get_stream_observation.assert_called_once_with(stream, mock_fn)
    mock_update_current_observation.assert_called_once_with(
        **mock_get_stream_observation.return_value,
        usage=ModelUsage(
            input=stream.input_tokens,
            output=stream.output_tokens,
            unit="TOKENS",
        ),
        output=result.constructed_response_model,
    )
