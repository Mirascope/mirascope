"""The `BaseCall` class for LLM calls."""

from abc import ABC
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic

from typing_extensions import TypeVar

from ..models import LLM
from ..prompts import AsyncPrompt, Prompt
from ..tools import ToolDef
from ..types import Jsonable, P

PromptT = TypeVar("PromptT", bound=Prompt | AsyncPrompt)


@dataclass
class BaseCall(Generic[P, PromptT], ABC):
    """A base class for generating responses using LLMs."""

    model: LLM
    """The LLM model used for generating responses."""

    tools: Sequence[ToolDef[..., Jsonable]] | None
    """The tools to be used with the LLM."""

    fn: PromptT
    """The Prompt function that generates the Prompt."""
