from collections.abc import Callable
from functools import reduce, wraps
from typing import Any, ParamSpec, TypeVar

_P = ParamSpec("_P")
_R = TypeVar("_R")

_WP = ParamSpec("_WP")
_WR = TypeVar("_WR")


def merge_decorators(
    decorator: Callable[[Callable[_P, _R]], Callable[_WP, _WR]],
    *additional_decorators: Callable[[Callable], Callable],
) -> Callable[[], Callable[[Callable[_P, _R]], Callable[_WP, _WR]]]:
    """Combines multiple decorators into a single decorator factory.

    This function allows you to merge multiple decorators into a single decorator factory.
    The decorators are applied in the order they are passed to the function.
    All function metadata (e.g. docstrings, function name) is preserved through the decoration chain.

    Args:
        decorator: The base decorator that determines the type signature of the decorated function.
        *additional_decorators: Additional decorators to be merged with the base decorator.

    Returns:
        A decorator factory function that applies all decorators in the specified order.

    Example:
        ```python
        # Combine multiple decorators
        merged = merge_decorators(
            retry(),
            with_logging(),
            handle_errors()
        )

        # Apply the merged decorators
        @merged()
        def my_function():
            pass
        ```
    """
    decorators = [decorator] + list(additional_decorators)

    def decorator_factory() -> Callable[[Callable[_P, _R]], Callable[_WP, _WR]]:
        def inner(func: Callable[_P, _R]) -> Callable[_WP, _WR]:
            def compose(f: Callable, d: Callable) -> Callable:
                @wraps(f)
                def wrapped(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
                    return d(f)(*args, **kwargs)

                return wrapped

            return reduce(compose, reversed(decorators), func)  # pyright: ignore [reportReturnType]

        return inner

    return decorator_factory
