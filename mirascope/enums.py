"""Enum Classes for mirascope."""
from enum import Enum, EnumMeta
from typing import Any


class _Metaclass(EnumMeta):
    """Base `EnumMeta` subclass for accessing enum members directly."""

    def __getattribute__(cls, __name: str) -> Any:
        value = super().__getattribute__(__name)
        if isinstance(value, Enum):
            value = value.value
        return value


class _Enum(str, Enum, metaclass=_Metaclass):
    """Base Enum Class."""


class MirascopeCommand(_Enum):
    """CLI commands to be executed."""

    ADD = "add"
    USE = "use"
    STATUS = "status"
    INIT = "init"
