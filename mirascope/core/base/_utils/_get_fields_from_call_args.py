"""Get FromCallArgs() annotated fields from a function call's args/kwargs."""

import inspect
from collections.abc import Callable
from typing import Any, get_origin

from pydantic import BaseModel

from mirascope.core.base._utils import get_fn_args
from mirascope.core.base.from_call_args import is_from_call_args


def get_fields_from_call_args(
    response_model: object,
    fn: Callable,
    args: tuple[object, ...],
    kwargs: dict[str, Any],
) -> dict[str, Any]:
    if origin := get_origin(response_model):
        response_model = origin
    if not (inspect.isclass(response_model) and issubclass(response_model, BaseModel)):
        return {}
    call_args_fields = {
        name
        for name, field in response_model.model_fields.items()
        if is_from_call_args(field)
    }

    fn_args = get_fn_args(fn, args, kwargs)
    if not call_args_fields.issubset(fn_args.keys()):
        raise ValueError(
            f"The function arguments do not contain all the fields marked with `FromCallArgs`. {fn_args=}, {call_args_fields=}"
        )
    return {name: fn_args[name] for name in call_args_fields}
