"""Internal utility functions for the Mirascope."""

import inspect
from collections.abc import Callable
from typing import Any, TypeAlias

import orjson

from .protocols import P, fn_wants_span

ORJSON_OPTS = (
    orjson.OPT_NON_STR_KEYS
    | orjson.OPT_NAIVE_UTC
    | orjson.OPT_SERIALIZE_NUMPY
    | orjson.OPT_SERIALIZE_DATACLASS
    | orjson.OPT_SERIALIZE_UUID
)

PrimitiveType: TypeAlias = str | int | float | bool


def json_dumps(obj: Any) -> str:  # noqa: ANN401
    """Serialize Python objects to JSON using orjson."""
    # json should be utf-8 encoded, json key should be str
    return orjson.dumps(obj, option=ORJSON_OPTS).decode("utf-8")


def get_qualified_name(fn: Callable[..., Any]) -> str:
    """Return the simplified qualified name of a function.

    If the function is defined locally, return the name after '<locals>.'; otherwise,
    return the last non-empty part after splitting by '.'.
    """
    qualified_name = fn.__qualname__
    if "<locals>." in qualified_name:
        return qualified_name.split("<locals>.")[-1]
    else:
        parts = [part for part in qualified_name.split(".") if part]
        return parts[-1] if parts else qualified_name


def extract_arguments(
    fn: Callable[P, Any],
    *args: P.args,
    **kwargs: P.kwargs,
) -> tuple[dict[str, str], dict[str, Any]]:
    """Returns a tuple of (arg_types, arg_values) dictionaries from function call.

    If the function has `trace_ctx: Span` as first parameter (detected via
    fn_wants_span), that parameter is skipped since it's injected by the
    decorator and shouldn't be recorded in span attributes.
    """
    signature = inspect.signature(fn)

    # If function wants span injection, skip the first parameter
    if fn_wants_span(fn):
        params = list(signature.parameters.values())
        if params:
            remaining_params = params[1:]
            signature = signature.replace(parameters=remaining_params)

    bound_arguments = signature.bind(*args, **kwargs)
    bound_arguments.apply_defaults()

    arg_types: dict[str, str] = {}
    arg_values: dict[str, Any] = {}

    for param_name, param_value in bound_arguments.arguments.items():
        parameter = signature.parameters[param_name]
        if parameter.annotation != inspect.Parameter.empty:
            if hasattr(parameter.annotation, "__name__"):
                type_str = parameter.annotation.__name__
            else:
                type_str = str(parameter.annotation)
            arg_types[param_name] = type_str
        else:
            arg_types[param_name] = type(param_value).__name__

        if isinstance(param_value, PrimitiveType) or param_value is None:
            arg_values[param_name] = param_value
        else:
            try:
                json_dumps(param_value)
                arg_values[param_name] = param_value
            except (TypeError, ValueError):
                arg_values[param_name] = repr(param_value)

    return arg_types, arg_values
