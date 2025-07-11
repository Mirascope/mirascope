"""The `BaseContextCall` class for LLM calls."""

from abc import ABC
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic

from ..models import LLM
from ..prompts import PromptT
from ..tools import ContextToolDef
from ..types import DepsT, FormatT, Jsonable, P


@dataclass
class BaseContextCall(Generic[P, PromptT, DepsT, FormatT], ABC):
    """A base class for generating responses with context using LLMs."""

    model: LLM
    """The LLM model used for generating responses."""

    tools: Sequence[ContextToolDef[..., Jsonable, DepsT]] | None
    """The tools to be used with the LLM."""

    response_format: type[FormatT] | None
    """The response format for the generated response."""

    fn: PromptT
    """The Prompt function that generates the Prompt."""
