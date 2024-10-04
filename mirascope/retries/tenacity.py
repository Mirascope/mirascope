"""Utitlies for more easily using Tenacity to reinsert errors on failed API calls."""

from collections.abc import Callable

from tenacity import RetryCallState


def collect_errors(
    *args: type[Exception],
) -> Callable[[RetryCallState], None]:
    """Collects specified errors into an `errors` keyword argument.

    Example:

    ```python
    from mirascope.integrations.tenacity import collect_errors
    from tenacity import retry, stop_after_attempt

    @retry(stop=stop_after_attempt(3), after=collect_errors(ValueError))
    def throw_value_error(*, errors: list[ValueError] | None = None):
        if errors:
            print(errors[-1])
        raise ValueError("Throwing Error")


    try:
        throw_value_error()
        # > Throwing Error
        # > Throwing Error
    except RetryError:
        ...
    ```

    Args:
        *args: The `Exception` types to catch.
    """

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
