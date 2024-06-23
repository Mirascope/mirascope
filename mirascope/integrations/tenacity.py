"""Mirascope x Tenacity Integration."""

from tenacity import RetryCallState


def collect_errors(retry_state: RetryCallState) -> None:
    """Collect errors into an `errors` keyword argument of the wrapped function."""
    if (outcome := retry_state.outcome) and (exception := outcome.exception()):
        errors = retry_state.kwargs.pop("errors", [])
        retry_state.kwargs["errors"] = errors + [exception] if errors else [exception]
