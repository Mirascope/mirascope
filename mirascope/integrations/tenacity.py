"""Mirascope x Tenacity Integration."""

from typing import Callable

from pydantic import ValidationError
from tenacity import RetryCallState

ExceptionType = type[Exception] | tuple[type[Exception], ...]


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


def collect_errors(
    error_types: list[ExceptionType],
) -> Callable[[RetryCallState], None]:
    def inner(retry_state: RetryCallState) -> None:
        """Collect errors into a `errors` kwarg of the wrapped function."""
        if (
            (outcome := retry_state.outcome)
            and (exception := outcome.exception())
            and type(exception) in error_types
        ):
            errors = retry_state.kwargs.pop("errors", [])
            retry_state.kwargs["errors"] = (
                errors + [exception] if errors else [exception]
            )

    return inner
