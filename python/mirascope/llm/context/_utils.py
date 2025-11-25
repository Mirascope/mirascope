import inspect
from collections.abc import Callable
from typing import Any, get_origin

from .context import Context


def first_param_is_context(fn: Callable[..., Any]) -> bool:
    """Returns whether the first argument to a function is `ctx: Context`.

    Also returns true if the first argument is a subclass of `Context`.
    Skips the first argument if it is `self` or `cls`.
    """
    sig = inspect.signature(fn)
    params = list(sig.parameters.values())
    if not params:
        return False

    if params[0].name in ("self", "cls") and len(params) > 1:
        first_param = params[1]
    else:
        first_param = params[0]

    type_is_context = get_origin(first_param.annotation) is Context
    subclass_of_context = isinstance(first_param.annotation, type) and issubclass(
        first_param.annotation, Context
    )
    return first_param.name == "ctx" and (type_is_context or subclass_of_context)
