from unittest.mock import MagicMock, patch

from mirascope.integrations.logfire import _utils
from mirascope.integrations.logfire._with_logfire import with_logfire


@patch(
    "mirascope.integrations.logfire._with_logfire.middleware_factory",
    new_callable=MagicMock,
)
def test_with_logfire(mock_middleware_factory: MagicMock) -> None:
    """Tests the `with_logfire` decorator."""
    mock_fn = MagicMock()
    with_logfire()(mock_fn)
    mock_middleware_factory.assert_called_once()
    call_args = mock_middleware_factory.call_args[1]
    assert call_args["custom_context_manager"] == _utils.custom_context_manager
    assert call_args["handle_response_model"] == _utils.handle_response_model
    assert (
        call_args["handle_response_model_async"] == _utils.handle_response_model_async
    )
    assert call_args["handle_call_response"] == _utils.handle_call_response
    assert call_args["handle_call_response_async"] == _utils.handle_call_response_async
    assert call_args["handle_stream"] == _utils.handle_stream
    assert call_args["handle_stream_async"] == _utils.handle_stream_async
    assert call_args["handle_error"] == _utils.handle_error
    assert call_args["handle_error_async"] == _utils.handle_error_async
