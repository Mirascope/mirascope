"""The `BaseStructuredCall` class for structured LLM calls."""

from abc import ABC
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic, ParamSpec

from typing_extensions import TypeVar

from ..models import LLM
from ..prompt import AsyncPromptable, Promptable
from ..tools import ToolDef
from ..types import Dataclass, Jsonable

P = ParamSpec("P")
T = TypeVar("T", bound=Dataclass | None, default=None)
PromptT = TypeVar("PromptT", bound=Promptable | AsyncPromptable)


@dataclass
class BaseStructuredCall(Generic[P, PromptT, T], ABC):
    """A base class for generating responses using LLMs."""

    model: LLM
    """The LLM model used for generating responses."""

    tools: Sequence[ToolDef[..., Jsonable]] | None
    """The tools to be used with the LLM."""

    response_format: type[T]
    """The response format for the generated response."""

    fn: PromptT
    """The function that generates the prompt template."""
