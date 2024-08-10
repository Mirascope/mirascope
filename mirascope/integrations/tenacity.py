"""Mirascope x Tenacity Integration."""

from typing import Callable

from tenacity import RetryCallState


def collect_errors(
    *args: type[Exception],
) -> Callable[[RetryCallState], None]:
    def inner(retry_state: RetryCallState) -> None:
        """Collect errors into a `errors` kwarg of the wrapped function."""
        if (
            (outcome := retry_state.outcome)
            and (exception := outcome.exception())
            and type(exception) in args
        ):
            errors = retry_state.kwargs.pop("errors", [])
            retry_state.kwargs["errors"] = (
                errors + [exception] if errors else [exception]
            )

    return inner
