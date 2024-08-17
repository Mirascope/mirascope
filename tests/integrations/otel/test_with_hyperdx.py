import os
from unittest.mock import MagicMock, patch

import pytest

from mirascope.integrations.otel._with_hyperdx import with_hyperdx


@pytest.fixture
def mock_env_variable():
    with patch.dict(os.environ, {"HYPERDX_API_KEY": "test-api-key"}):
        yield


@patch(
    "mirascope.integrations.otel._with_hyperdx.with_otel",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.otel._with_hyperdx.trace",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.otel._with_hyperdx.configure",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.otel._with_hyperdx.BatchSpanProcessor",
    new_callable=MagicMock,
)
@patch(
    "mirascope.integrations.otel._with_hyperdx.OTLPSpanExporter", new_callable=MagicMock
)
def test_with_hyperdx(
    mock_otlp_span_exporter: MagicMock,
    mock_batch_span_processor: MagicMock,
    mock_configure: MagicMock,
    mock_trace: MagicMock,
    mock_with_otel: MagicMock,
    mock_env_variable,
) -> None:
    """Tests the `with_hyperdx` decorator."""
    mock_trace.get_tracer_provider.return_value = MagicMock()
    mock_fn = MagicMock()
    with_hyperdx()(mock_fn)
    mock_with_otel.assert_called_once()
    mock_otlp_span_exporter.assert_called_once_with(
        endpoint="https://in-otel.hyperdx.io/v1/traces",
        headers={"authorization": "test-api-key"},
    )
    mock_batch_span_processor.assert_called_once_with(
        mock_otlp_span_exporter.return_value
    )
    mock_configure.assert_called_once_with(
        processors=[mock_batch_span_processor.return_value]
    )
