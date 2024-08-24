"""Function for binding `args` and `kwargs` as a dictionary to the fn's signature."""

import inspect
from collections.abc import Callable
from typing import Any


def get_fn_args(
    fn: Callable, args: tuple[object, ...], kwargs: dict[str, Any]
) -> dict[str, Any]:
    """Returns the `args` and `kwargs` as a dictionary bound by `fn`'s signature."""
    signature = inspect.signature(fn)
    bound_args = signature.bind_partial(*args, **kwargs)
    bound_args.apply_defaults()

    fn_args = {}
    for name, value in bound_args.arguments.items():
        if signature.parameters[name].kind == inspect.Parameter.VAR_KEYWORD:
            fn_args.update(value)
        else:
            fn_args[name] = value

    return fn_args
