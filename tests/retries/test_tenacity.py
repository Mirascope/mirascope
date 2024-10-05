from unittest.mock import MagicMock

from pydantic import BaseModel, ValidationError
from tenacity import RetryCallState

from mirascope.retries.tenacity import collect_errors


def test_collect_errors() -> None:
    validation_error = None
    try:

        class Foo(BaseModel):
            bar: str

        Foo(bar=1)  # type: ignore
    except ValidationError as e:
        validation_error = e
    mock_retry_state = MagicMock(spec=RetryCallState)
    outcome = MagicMock()
    mock_retry_state.outcome = outcome
    mock_retry_state.kwargs = {}
    outcome.exception.return_value = validation_error
    collect_errors(ValidationError)(mock_retry_state)
    assert mock_retry_state.kwargs["errors"] == [validation_error]
