"""The `BaseCall` class for LLM calls."""

from abc import ABC
from dataclasses import dataclass
from typing import Generic

from ..formatting import FormatT
from ..models import LLM
from ..prompts import PromptT
from ..tools import ToolkitT
from ..types import P


@dataclass
class BaseCall(Generic[P, PromptT, ToolkitT, FormatT], ABC):
    """A base class for generating responses using LLMs."""

    model: LLM
    """The LLM model used for generating responses."""

    toolkit: ToolkitT
    """The toolkit containing this call's tools."""

    format: type[FormatT] | None
    """The response format for the generated response."""

    fn: PromptT
    """The Prompt function that generates the Prompt."""
