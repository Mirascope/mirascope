from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from mirascope.core.base.call_response import BaseCallResponse
from mirascope.core.base.metadata import Metadata
from mirascope.core.base.stream import BaseStream
from mirascope.core.base.structured_stream import BaseStructuredStream
from mirascope.integrations.langfuse import _utils
from mirascope.integrations.langfuse._utils import ModelUsage


def test_get_call_response_observation() -> None:
    """Tests the `_get_call_response_observation` function."""
    mock_result = MagicMock(spec=BaseCallResponse)
    mock_result.model = "test_model"
    mock_result.messages = "test_messages"
    mock_result.response = "test_response"
    mock_result.message_param = {"role": "assistant", "content": "test_content"}
    mock_fn = MagicMock(__name__="mock_fn")
    mock_fn._metadata = Metadata(tags={"tag1"})
    call_response_observation = _utils._get_call_response_observation(
        mock_result, mock_fn
    )
    assert call_response_observation["name"] == "mock_fn with test_model"
    assert call_response_observation["input"] == "test_messages"
    assert call_response_observation["metadata"] == "test_response"
    assert call_response_observation["tags"] == {"tag1"}
    assert call_response_observation["model"] == "test_model"
    assert call_response_observation["output"] == "test_content"


@patch(
    "mirascope.integrations.langfuse._utils.langfuse_context.update_current_observation",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse._utils._get_call_response_observation",
    new_callable=MagicMock,
)
def test_handle_call_response(
    mock_get_call_response_observation: MagicMock,
    mock_update_current_observation: MagicMock,
) -> None:
    """Tests the `handle_call_response` function."""
    mock_fn = MagicMock(__name__="mock_fn")

    result = MagicMock(spec=BaseCallResponse)
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
    "mirascope.integrations.langfuse._utils._get_call_response_observation",
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
    "mirascope.integrations.langfuse._utils._get_call_response_observation",
    new_callable=MagicMock,
)
def test_handle_stream(
    mock_get_call_response_observation: MagicMock,
    mock_update_current_observation: MagicMock,
) -> None:
    """Tests the `handle_stream` function."""
    mock_fn = MagicMock(__name__="mock_fn")

    result = MagicMock(spec=BaseStream)
    mock_construct_call_response = MagicMock()
    mock_construct_call_response_return_value = {}
    mock_construct_call_response.return_value = (
        mock_construct_call_response_return_value
    )
    result.construct_call_response = mock_construct_call_response
    _utils.handle_stream(result, mock_fn, None)
    mock_get_call_response_observation.assert_called_once_with(
        mock_construct_call_response(), mock_fn
    )
    mock_update_current_observation.assert_called_once_with(
        **mock_construct_call_response_return_value,
        usage=ModelUsage(
            input=result.input_tokens,
            output=result.output_tokens,
            unit="TOKENS",
        ),
    )


@patch(
    "mirascope.integrations.langfuse._utils.handle_stream",
    new_callable=MagicMock,
)
@pytest.mark.asyncio
async def test_handle_stream_async(
    mock_handle_stream: MagicMock,
) -> None:
    """Tests the `handle_stream_async` function."""
    mock_fn = MagicMock(__name__="mock_fn")

    result = MagicMock(spec=BaseStream)
    await _utils.handle_stream_async(result, mock_fn, None)
    mock_handle_stream.assert_called_once_with(result, mock_fn, None)


@patch(
    "mirascope.integrations.langfuse._utils.langfuse_context.update_current_observation",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse._utils._get_call_response_observation",
    new_callable=MagicMock,
)
def test_handle_response_model(
    mock_get_call_response_observation: MagicMock,
    mock_update_current_observation: MagicMock,
) -> None:
    """Tests the `handle_response_model` function."""
    mock_fn = MagicMock(__name__="mock_fn")
    result = MagicMock(spec=BaseModel)
    response = MagicMock(spec=BaseCallResponse)
    result._response = response

    _utils.handle_response_model(result, mock_fn, None)
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
def test_handle_response_model_base_type(
    mock_update_current_observation: MagicMock,
) -> None:
    """Tests the `handle_response_model` function with `BaseType` result."""
    mock_fn = MagicMock(__name__="mock_fn")
    result = MagicMock(spec=str)

    _utils.handle_response_model(result, mock_fn, None)
    mock_update_current_observation.assert_called_once_with(
        output=result,
    )


@patch(
    "mirascope.integrations.langfuse._utils.langfuse_context.update_current_observation",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse._utils._get_call_response_observation",
    new_callable=MagicMock,
)
def test_handle_structured_stream(
    mock_get_call_response_observation: MagicMock,
    mock_update_current_observation: MagicMock,
) -> None:
    """Tests the `handle_structured_stream` function."""
    mock_fn = MagicMock(__name__="mock_fn")
    result = MagicMock(spec=BaseStructuredStream)
    result.constructed_response_model = MagicMock()
    stream = MagicMock(spec=BaseStream)
    result.stream = stream
    mock_construct_call_response = MagicMock()
    mock_construct_call_response_return_value = {}
    mock_construct_call_response.return_value = (
        mock_construct_call_response_return_value
    )
    stream.construct_call_response = mock_construct_call_response
    _utils.handle_structured_stream(result, mock_fn, None)
    mock_get_call_response_observation.assert_called_once_with(
        mock_construct_call_response(), mock_fn
    )
    mock_update_current_observation.assert_called_once_with(
        **mock_construct_call_response_return_value,
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
    "mirascope.integrations.langfuse._utils._get_call_response_observation",
    new_callable=MagicMock,
)
@pytest.mark.asyncio
async def test_handle_response_model_async(
    mock_get_call_response_observation: MagicMock,
    mock_update_current_observation: MagicMock,
) -> None:
    """Tests the `handle_response_model` function."""
    mock_fn = MagicMock(__name__="mock_fn")
    result = MagicMock(spec=BaseModel)
    response = MagicMock(spec=BaseCallResponse)
    result._response = response

    await _utils.handle_response_model_async(result, mock_fn, None)
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
    "mirascope.integrations.langfuse._utils.handle_structured_stream",
    new_callable=MagicMock,
)
@pytest.mark.asyncio
async def test_handle_structured_stream_async(
    mock_handle_structured_stream: MagicMock,
) -> None:
    """Tests the `handle_structured_stream_async` function."""
    mock_fn = MagicMock(__name__="mock_fn")
    result = MagicMock(spec=BaseStructuredStream)

    await _utils.handle_structured_stream_async(result, mock_fn, None)
    mock_handle_structured_stream.assert_called_once_with(result, mock_fn, None)
