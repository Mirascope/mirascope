"""Function for binding `args` and `kwargs` as a dictionary to the fn's signature."""

import inspect
from typing import Any, Callable


def get_fn_args(
    fn: Callable, args: tuple[object, ...], kwargs: dict[str, Any]
) -> dict[str, Any]:
    """Returns the `args` and `kwargs` as a dictionary bound by `fn`'s signature."""
    bound_args = inspect.signature(fn).bind_partial(*args, **kwargs)
    bound_args.apply_defaults()
    return bound_args.arguments
