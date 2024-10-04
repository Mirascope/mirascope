import inspect
from collections.abc import Callable

from pydantic import BaseModel

from mirascope.core.base.from_call_args import is_from_call_args


def get_call_args_field_names_and_validate(
    response_model: object, fn: Callable
) -> set[str]:
    if not (inspect.isclass(response_model) and issubclass(response_model, BaseModel)):
        return set()
    call_args_fields = {
        name
        for name, field in response_model.model_fields.items()
        if is_from_call_args(field)
    }

    signature = inspect.signature(fn)
    arguments = signature.parameters.keys()
    if not call_args_fields.issubset(arguments):
        raise ValueError(
            f"The function arguments do not contain all the fields marked with `FromCallArgs`. {arguments=}, {call_args_fields=}"
        )
    return call_args_fields
