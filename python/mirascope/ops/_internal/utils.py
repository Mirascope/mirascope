"""Internal utility functions for the Mirascope."""

from collections.abc import Callable
from typing import Any

import orjson

ORJSON_OPTS = (
    orjson.OPT_NON_STR_KEYS
    | orjson.OPT_NAIVE_UTC
    | orjson.OPT_SERIALIZE_NUMPY
    | orjson.OPT_SERIALIZE_DATACLASS
    | orjson.OPT_SERIALIZE_UUID
)


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
