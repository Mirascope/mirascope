"""The `BaseCall` class for LLM calls."""

from abc import ABC
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Generic, ParamSpec

from typing_extensions import TypeVar

from ..messages import PromptTemplate
from ..models import LLM
from ..tools import ToolDef

P = ParamSpec("P")
T = TypeVar("T", default=None)


@dataclass
class BaseCall(Generic[P], ABC):
    """A base class for generating responses using LLMs."""

    model: LLM
    """The LLM model used for generating responses."""

    tools: Sequence[ToolDef] | None
    """The tools to be used with the LLM."""

    fn: Callable[P, PromptTemplate[P]]
    """The function that generates the prompt template."""
