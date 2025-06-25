"""The `BaseCall` class for LLM calls."""

from abc import ABC
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic, ParamSpec

from typing_extensions import TypeVar

from ..models import LLM
from ..prompt import AsyncPromptable, Promptable
from ..tools import ToolDef
from ..types import Jsonable

P = ParamSpec("P")
PromptT = TypeVar("PromptT", bound=Promptable | AsyncPromptable)


@dataclass
class BaseCall(Generic[P, PromptT], ABC):
    """A base class for generating responses using LLMs."""

    model: LLM
    """The LLM model used for generating responses."""

    tools: Sequence[ToolDef[..., Jsonable]] | None
    """The tools to be used with the LLM."""

    fn: PromptT
    """The function that generates the prompt template."""
