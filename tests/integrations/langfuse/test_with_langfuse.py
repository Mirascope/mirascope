from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from mirascope.core.base._stream import BaseStream
from mirascope.core.base._structured_stream import BaseStructuredStream
from mirascope.core.base.call_response import BaseCallResponse
from mirascope.integrations.langfuse.with_langfuse import ModelUsage, with_langfuse


@patch(
    "mirascope.integrations.langfuse.with_langfuse.middleware_decorator",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse.with_langfuse.observe",
    new_callable=MagicMock,
)
def test_with_langfuse(
    mock_observe: MagicMock, mock_middleware_decorator: MagicMock
) -> None:
    """Tests the `with_langfuse` decorator."""
    mock_fn = MagicMock(__name__="mock_fn")
    mock_observe.return_value = MagicMock()
    with_langfuse(mock_fn)
    mock_middleware_decorator.assert_called_once()
    mock_observe.assert_called_once_with(
        name=mock_fn.__name__,
        as_type="generation",
        capture_input=False,
        capture_output=False,
    )
    call_args = mock_middleware_decorator.call_args[1]
    assert call_args["custom_decorator"] == mock_observe.return_value
    assert call_args["handle_base_model"] is not None
    assert call_args["handle_base_model_async"] is not None
    assert call_args["handle_call_response"] is not None
    assert call_args["handle_call_response_async"] is not None
    assert call_args["handle_stream"] is not None
    assert call_args["handle_stream_async"] is not None
    assert mock_middleware_decorator.call_args[0][0] == mock_fn


@patch(
    "mirascope.integrations.langfuse.with_langfuse.middleware_decorator",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse.with_langfuse.observe",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse.with_langfuse.langfuse_context.update_current_observation",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse.with_langfuse.get_call_response_observation",
    new_callable=MagicMock,
)
def test_handle_call_response(
    mock_get_call_response_observation: MagicMock,
    mock_update_current_observation: MagicMock,
    mock_observe: MagicMock,
    mock_middleware_decorator: MagicMock,
) -> None:
    """Tests the `handle_call_response` function."""
    mock_fn = MagicMock(__name__="mock_fn")
    mock_observe.return_value = MagicMock()
    with_langfuse(mock_fn)
    handle_call_response = mock_middleware_decorator.call_args[1][
        "handle_call_response"
    ]

    result = MagicMock(spec=BaseCallResponse)
    result.input_tokens = 1
    result.output_tokens = 2
    handle_call_response(result, None)
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
    "mirascope.integrations.langfuse.with_langfuse.middleware_decorator",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse.with_langfuse.observe",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse.with_langfuse.langfuse_context.update_current_observation",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse.with_langfuse.get_call_response_observation",
    new_callable=MagicMock,
)
@pytest.mark.asyncio
async def test_handle_call_response_async(
    mock_get_call_response_observation: MagicMock,
    mock_update_current_observation: MagicMock,
    mock_observe: MagicMock,
    mock_middleware_decorator: MagicMock,
) -> None:
    """Tests the `handle_call_response` function."""
    mock_fn = MagicMock(__name__="mock_fn")
    mock_observe.return_value = MagicMock()
    with_langfuse(mock_fn)
    handle_call_response_async = mock_middleware_decorator.call_args[1][
        "handle_call_response_async"
    ]

    result = MagicMock(spec=BaseCallResponse)
    result.input_tokens = 1
    result.output_tokens = 2
    await handle_call_response_async(result, None)
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
    "mirascope.integrations.langfuse.with_langfuse.middleware_decorator",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse.with_langfuse.observe",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse.with_langfuse.langfuse_context.update_current_observation",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse.with_langfuse.get_stream_observation",
    new_callable=MagicMock,
)
def test_handle_stream(
    mock_get_stream_observation: MagicMock,
    mock_update_current_observation: MagicMock,
    mock_observe: MagicMock,
    mock_middleware_decorator: MagicMock,
) -> None:
    """Tests the `handle_call_response` function."""
    mock_fn = MagicMock(__name__="mock_fn")
    mock_observe.return_value = MagicMock()
    with_langfuse(mock_fn)
    handle_stream = mock_middleware_decorator.call_args[1]["handle_stream"]

    result = MagicMock(spec=BaseCallResponse)
    result.input_tokens = 1
    result.output_tokens = 2
    handle_stream(result, None)
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
    "mirascope.integrations.langfuse.with_langfuse.middleware_decorator",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse.with_langfuse.observe",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse.with_langfuse.langfuse_context.update_current_observation",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse.with_langfuse.get_stream_observation",
    new_callable=MagicMock,
)
@pytest.mark.asyncio
async def test_handle_stream_async(
    mock_get_stream_observation: MagicMock,
    mock_update_current_observation: MagicMock,
    mock_observe: MagicMock,
    mock_middleware_decorator: MagicMock,
) -> None:
    """Tests the `handle_call_response` function."""
    mock_fn = MagicMock(__name__="mock_fn")
    mock_observe.return_value = MagicMock()
    with_langfuse(mock_fn)
    handle_stream_async = mock_middleware_decorator.call_args[1]["handle_stream_async"]

    result = MagicMock(spec=BaseCallResponse)
    result.input_tokens = 1
    result.output_tokens = 2
    await handle_stream_async(result, None)
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
    "mirascope.integrations.langfuse.with_langfuse.middleware_decorator",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse.with_langfuse.observe",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse.with_langfuse.langfuse_context.update_current_observation",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse.with_langfuse.get_call_response_observation",
    new_callable=MagicMock,
)
def test_handle_base_model(
    mock_get_call_response_observation: MagicMock,
    mock_update_current_observation: MagicMock,
    mock_observe: MagicMock,
    mock_middleware_decorator: MagicMock,
) -> None:
    """Tests the `handle_base_model` function."""
    mock_fn = MagicMock(__name__="mock_fn")
    mock_observe.return_value = MagicMock()
    with_langfuse(mock_fn)
    handle_base_model = mock_middleware_decorator.call_args[1]["handle_base_model"]
    result = MagicMock(spec=BaseModel)
    result.input_tokens = 1
    result.output_tokens = 2
    response = MagicMock(spec=BaseCallResponse)
    result._response = response

    handle_base_model(result, None)
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
    "mirascope.integrations.langfuse.with_langfuse.middleware_decorator",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse.with_langfuse.observe",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse.with_langfuse.langfuse_context.update_current_observation",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse.with_langfuse.get_stream_observation",
    new_callable=MagicMock,
)
def test_handle_structured_stream(
    mock_get_stream_observation: MagicMock,
    mock_update_current_observation: MagicMock,
    mock_observe: MagicMock,
    mock_middleware_decorator: MagicMock,
) -> None:
    """Tests the `handle_base_model` function."""
    mock_fn = MagicMock(__name__="mock_fn")
    mock_observe.return_value = MagicMock()
    with_langfuse(mock_fn)
    handle_base_model = mock_middleware_decorator.call_args[1]["handle_base_model"]
    result = MagicMock(spec=BaseStructuredStream)
    result.input_tokens = 1
    result.output_tokens = 2
    result.constructed_response_model = MagicMock()
    stream = MagicMock(spec=BaseStream)
    result.stream = stream

    handle_base_model(result, None)
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
    "mirascope.integrations.langfuse.with_langfuse.middleware_decorator",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse.with_langfuse.observe",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse.with_langfuse.langfuse_context.update_current_observation",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse.with_langfuse.get_call_response_observation",
    new_callable=MagicMock,
)
@pytest.mark.asyncio
async def test_handle_base_model_async(
    mock_get_call_response_observation: MagicMock,
    mock_update_current_observation: MagicMock,
    mock_observe: MagicMock,
    mock_middleware_decorator: MagicMock,
) -> None:
    """Tests the `handle_base_model` function."""
    mock_fn = MagicMock(__name__="mock_fn")
    mock_observe.return_value = MagicMock()
    with_langfuse(mock_fn)
    handle_base_model_async = mock_middleware_decorator.call_args[1][
        "handle_base_model_async"
    ]
    result = MagicMock(spec=BaseModel)
    result.input_tokens = 1
    result.output_tokens = 2
    response = MagicMock(spec=BaseCallResponse)
    result._response = response

    await handle_base_model_async(result, None)
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
    "mirascope.integrations.langfuse.with_langfuse.middleware_decorator",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse.with_langfuse.observe",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse.with_langfuse.langfuse_context.update_current_observation",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.langfuse.with_langfuse.get_stream_observation",
    new_callable=MagicMock,
)
@pytest.mark.asyncio
async def test_handle_structured_stream_async(
    mock_get_stream_observation: MagicMock,
    mock_update_current_observation: MagicMock,
    mock_observe: MagicMock,
    mock_middleware_decorator: MagicMock,
) -> None:
    """Tests the `handle_base_model` function."""
    mock_fn = MagicMock(__name__="mock_fn")
    mock_observe.return_value = MagicMock()
    with_langfuse(mock_fn)
    handle_base_model_async = mock_middleware_decorator.call_args[1][
        "handle_base_model_async"
    ]
    result = MagicMock(spec=BaseStructuredStream)
    result.input_tokens = 1
    result.output_tokens = 2
    result.constructed_response_model = MagicMock()
    stream = MagicMock(spec=BaseStream)
    result.stream = stream

    await handle_base_model_async(result, None)
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
