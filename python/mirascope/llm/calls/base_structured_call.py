"""The `BaseStructuredCall` class for structured LLM calls."""

from abc import ABC
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic, ParamSpec

from typing_extensions import TypeVar

from ..models import LLM
from ..prompt_templates import AsyncPromptable, Promptable
from ..tools import ToolDef
from ..types import Jsonable

P = ParamSpec("P")
T = TypeVar("T", bound=object | None, default=None)
PromptableT = TypeVar("PromptableT", bound=Promptable | AsyncPromptable)


@dataclass
class BaseStructuredCall(Generic[P, PromptableT, T], ABC):
    """A base class for generating responses using LLMs."""

    model: LLM
    """The LLM model used for generating responses."""

    tools: Sequence[ToolDef[..., Jsonable]] | None
    """The tools to be used with the LLM."""

    response_format: type[T]
    """The response format for the generated response."""

    fn: PromptableT
    """The Promptable function that generates the Prompt."""
