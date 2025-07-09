"""The `BaseStructuredContextCall` class for structured context LLM calls."""

from abc import ABC
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic

from typing_extensions import TypeVar

from ..models import LLM
from ..prompts import AsyncPrompt, Prompt
from ..tools import ContextToolDef
from ..types import DepsT, Jsonable, P

T = TypeVar("T", bound=object | None, default=None)
PromptT = TypeVar("PromptT", bound=Prompt | AsyncPrompt)


@dataclass
class BaseStructuredContextCall(Generic[P, PromptT, T, DepsT], ABC):
    """A base class for generating responses using LLMs."""

    model: LLM
    """The LLM model used for generating responses."""

    tools: Sequence[ContextToolDef[..., Jsonable, DepsT]] | None
    """The tools to be used with the LLM."""

    response_format: type[T]
    """The response format for the generated response."""

    fn: PromptT
    """The Prompt function that generates the Prompt."""
