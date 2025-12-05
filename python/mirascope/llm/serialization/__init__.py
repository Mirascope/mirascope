"""Serialization and deserialization for Mirascope responses."""

from typing import TYPE_CHECKING

from ._generated.response import (
    SerializedFormat,
    SerializedToolSchema,
    ToolParameterSchema as SerializedToolParameterSchema,
)
from .encoder import encode, encode_str
from .exceptions import (
    IncompatibleFormatError,
    IncompatibleToolsError,
    IncompatibleVersionError,
    InvalidSerializedDataError,
    SchemaMismatchError,
    SerializationError,
    UnknownContentTypeError,
    UnknownMessageRoleError,
)
from .version import CURRENT_VERSION, SerializationVersion, get_current_version

if TYPE_CHECKING:
    from .decoder import decode as decode

__all__ = [
    "CURRENT_VERSION",
    "IncompatibleFormatError",
    "IncompatibleToolsError",
    "IncompatibleVersionError",
    "InvalidSerializedDataError",
    "SchemaMismatchError",
    "SerializationError",
    "SerializationVersion",
    "SerializedFormat",
    "SerializedToolParameterSchema",
    "SerializedToolSchema",
    "UnknownContentTypeError",
    "UnknownMessageRoleError",
    "decode",
    "encode",
    "encode_str",
    "get_current_version",
]


def __getattr__(name: str):  # noqa: ANN202
    """Lazy import decode to avoid circular imports."""
    if name == "decode":
        from .decoder import decode

        return decode
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
