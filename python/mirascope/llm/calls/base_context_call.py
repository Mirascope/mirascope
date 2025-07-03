"""The `BaseContextCall` class for LLM calls."""

from abc import ABC
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic, ParamSpec

from typing_extensions import TypeVar

from ..models import LLM
from ..prompts import AsyncPrompt, Prompt
from ..tools import ContextToolDef
from ..types import Jsonable

P = ParamSpec("P")
PromptT = TypeVar("PromptT", bound=Prompt | AsyncPrompt)
DepsT = TypeVar("DepsT", default=None)


@dataclass
class BaseContextCall(Generic[P, PromptT, DepsT], ABC):
    """A base class for generating responses with context using LLMs."""

    model: LLM
    """The LLM model used for generating responses."""

    tools: Sequence[ContextToolDef[..., Jsonable, DepsT]] | None
    """The tools to be used with the LLM."""

    fn: PromptT
    """The Prompt function that generates the Prompt."""
