"""The `BaseContextCall` class for LLM calls."""

from abc import ABC
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic

from ..models import LLM
from ..tools import ContextToolDef
from ..types import DepsT, Jsonable, P, PromptT


@dataclass
class BaseContextCall(Generic[P, PromptT, DepsT], ABC):
    """A base class for generating responses with context using LLMs."""

    model: LLM
    """The LLM model used for generating responses."""

    tools: Sequence[ContextToolDef[..., Jsonable, DepsT]] | None
    """The tools to be used with the LLM."""

    fn: PromptT
    """The Prompt function that generates the Prompt."""
