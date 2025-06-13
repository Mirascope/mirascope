"""A protocol for defining a dataclass type."""

from dataclasses import Field
from typing import Any, ClassVar, Protocol


class Dataclass(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]
