from unittest.mock import MagicMock, patch

from mirascope.integrations.otel import _utils
from mirascope.integrations.otel._with_otel import with_otel


@patch(
    "mirascope.integrations.otel._with_otel.middleware_factory",
    new_callable=MagicMock,
)
def test_with_otel(mock_middleware_factory: MagicMock) -> None:
    """Tests the `with_otel` decorator."""
    mock_fn = MagicMock()
    with_otel()(mock_fn)
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
