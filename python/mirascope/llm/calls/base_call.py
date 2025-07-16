"""The `BaseCall` class for LLM calls."""

from abc import ABC
from dataclasses import dataclass
from typing import Generic

from ..models import LLM
from ..prompts import PromptT
from ..response_formatting import FormatT
from ..tools import Toolkit, ToolT
from ..types import P


@dataclass
class BaseCall(Generic[P, PromptT, ToolT, FormatT], ABC):
    """A base class for generating responses using LLMs."""

    model: LLM
    """The LLM model used for generating responses."""

    toolkit: Toolkit[ToolT]
    """The toolkit of tools associated with this call."""

    response_format: type[FormatT] | None
    """The response format for the generated response."""

    fn: PromptT
    """The Prompt function that generates the Prompt."""
