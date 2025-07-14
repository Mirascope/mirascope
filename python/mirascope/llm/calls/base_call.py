"""The `BaseCall` class for LLM calls."""

from abc import ABC
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic

from ..models import LLM
from ..prompts import PromptT
from ..response_formatting import FormatT
from ..tools import ToolDef
from ..types import Jsonable, P


@dataclass
class BaseCall(Generic[P, PromptT, FormatT], ABC):
    """A base class for generating responses using LLMs."""

    model: LLM
    """The LLM model used for generating responses."""

    tools: Sequence[ToolDef[..., Jsonable]] | None
    """The tools to be used with the LLM."""

    response_format: type[FormatT] | None
    """The response format for the generated response."""

    fn: PromptT
    """The Prompt function that generates the Prompt."""
