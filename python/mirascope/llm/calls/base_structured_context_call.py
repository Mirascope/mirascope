"""The `BaseStructuredContextCall` class for structured context LLM calls."""

from abc import ABC
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic, ParamSpec

from typing_extensions import TypeVar

from ..models import LLM
from ..prompts import AsyncPromptable, Promptable
from ..tools import ContextToolDef
from ..types import Jsonable

P = ParamSpec("P")
T = TypeVar("T", bound=object | None, default=None)
PromptableT = TypeVar("PromptableT", bound=Promptable | AsyncPromptable)
DepsT = TypeVar("DepsT", default=None)


@dataclass
class BaseStructuredContextCall(Generic[P, PromptableT, T, DepsT], ABC):
    """A base class for generating responses using LLMs."""

    model: LLM
    """The LLM model used for generating responses."""

    tools: Sequence[ContextToolDef[..., Jsonable, DepsT]] | None
    """The tools to be used with the LLM."""

    response_format: type[T]
    """The response format for the generated response."""

    fn: PromptableT
    """The Promptable function that generates the Prompt."""
