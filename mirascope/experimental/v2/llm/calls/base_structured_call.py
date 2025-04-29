"""The `BaseStructuredCall` class for structured LLM calls."""

from abc import ABC
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic, ParamSpec

from typing_extensions import TypeVar

from ..messages import AsyncPromptTemplate, PromptTemplate
from ..models import LLM
from ..tools import ToolDef

P = ParamSpec("P")
T = TypeVar("T", default=None)
PromptTemplateT = TypeVar("PromptTemplateT", bound=PromptTemplate | AsyncPromptTemplate)


@dataclass
class BaseStructuredCall(Generic[P, PromptTemplateT, T], ABC):
    """A base class for generating responses using LLMs."""

    model: LLM
    """The LLM model used for generating responses."""

    tools: Sequence[ToolDef] | None
    """The tools to be used with the LLM."""

    response_format: type[T]
    """The response format for the generated response."""

    fn: PromptTemplateT
    """The function that generates the prompt template."""
