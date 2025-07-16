"""The `BaseContextCall` class for LLM calls."""

from abc import ABC
from dataclasses import dataclass
from typing import Generic

from ..context import DepsT
from ..models import LLM
from ..prompts import PromptT
from ..response_formatting import FormatT
from ..tools import ContextToolkit, ContextToolT
from ..types import P


@dataclass
class BaseContextCall(Generic[P, PromptT, ContextToolT, DepsT, FormatT], ABC):
    """A base class for generating responses with context using LLMs."""

    model: LLM
    """The LLM model used for generating responses."""

    toolkit: ContextToolkit[ContextToolT, DepsT]

    response_format: type[FormatT] | None
    """The response format for the generated response."""

    fn: PromptT
    """The Prompt function that generates the Prompt."""
