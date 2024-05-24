import os
from unittest.mock import MagicMock, patch


from mirascope.otel.hyperdx.hyperdx import with_hyperdx


@patch("opentelemetry.trace.get_tracer_provider", new_callable=MagicMock)
@patch("mirascope.otel.otel.configure", new_callable=MagicMock)
def test_hyperdx_decorator(
    mock_configure: MagicMock, mock_get_tracer_provider: MagicMock
) -> None:
    """Test that when trace provider is not set, we auto configure it with HyperDX"""
    os.environ["HYPERDX_API_KEY"] = "test"
    mock_get_tracer_provider.return_value = None

    @with_hyperdx
    def test_function():
        ...

    test_function()

    actual_call = mock_configure.call_args_list[0]
    actual_processors = actual_call.kwargs["processors"]
    assert (
        actual_processors[0].span_exporter._endpoint
        == "https://in-otel.hyperdx.io/v1/traces"
    )
    assert actual_processors[0].span_exporter._headers == {"authorization": "test"}
