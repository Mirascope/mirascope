"""The `BaseStructuredCall` class for structured LLM calls."""

from abc import ABC
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic, ParamSpec

from typing_extensions import TypeVar

from ..models import LLM
from ..prompt_templates import AsyncPromptTemplate, PromptTemplate
from ..tools import ToolDef
from ..types import Dataclass, Jsonable

P = ParamSpec("P")
T = TypeVar("T", bound=Dataclass | None, default=None)
PromptTemplateT = TypeVar("PromptTemplateT", bound=PromptTemplate | AsyncPromptTemplate)


@dataclass
class BaseStructuredCall(Generic[P, PromptTemplateT, T], ABC):
    """A base class for generating responses using LLMs."""

    model: LLM
    """The LLM model used for generating responses."""

    tools: Sequence[ToolDef[..., Jsonable]] | None
    """The tools to be used with the LLM."""

    response_format: type[T]
    """The response format for the generated response."""

    fn: PromptTemplateT
    """The function that generates the prompt template."""
