"""Mirascope x Tenacity Integration."""

from pydantic import ValidationError
from tenacity import RetryCallState


def collect_validation_errors(retry_state: RetryCallState) -> None:
    """Collect errors into a `validation_errors` kwarg of the wrapped function."""
    if (
        (outcome := retry_state.outcome)
        and (exception := outcome.exception())
        and type(exception) == ValidationError
    ):
        errors = retry_state.kwargs.pop("validation_errors", [])
        retry_state.kwargs["validation_errors"] = (
            errors + [exception] if errors else [exception]
        )
