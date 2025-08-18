"""The `BaseCall` class for LLM calls."""

from abc import ABC
from dataclasses import dataclass
from typing import Generic

from ..formatting import FormatT
from ..models import LLM, get_model_from_context
from ..prompts import PromptT
from ..tools import ToolkitT
from ..types import P


@dataclass
class BaseCall(Generic[P, PromptT, ToolkitT, FormatT], ABC):
    """A base class for generating responses using LLMs."""

    default_model: LLM
    """The default model that will be used if no model is set in context."""

    toolkit: ToolkitT
    """The toolkit containing this call's tools."""

    format: type[FormatT] | None
    """The response format for the generated response."""

    fn: PromptT
    """The Prompt function that generates the Prompt."""

    @property
    def model(self) -> LLM:
        """The model used for generating responses. May be overwritten via `with llm.model(...)."""
        return get_model_from_context() or self.default_model
