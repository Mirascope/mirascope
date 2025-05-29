"""BaseTool class for LLM tools."""

from abc import ABC
from dataclasses import dataclass
from typing import Generic, ParamSpec, TypeVar

from ..types import Jsonable

P = ParamSpec("P")
R = TypeVar("R", bound=Jsonable)


@dataclass
class BaseTool(Generic[P, R], ABC):
    """Tool instance with arguments provided by an LLM.

    When an LLM uses a tool during a call, a Tool instance is created with the specific
    arguments provided by the LLM.
    """

    name: str
    """The name of the tool being called."""

    args: dict[str, Jsonable]
    """The arguments provided by the LLM for this tool call."""

    id: str
    """Unique identifier for this tool call."""
