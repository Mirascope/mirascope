"""The `BaseAgent` class for LLM agents."""

from abc import ABC
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic

from typing_extensions import TypeVar

from ..context import Context
from ..models import LLM
from ..tools import ToolDef

DepsT = TypeVar("DepsT", default=None)


@dataclass
class BaseAgent(Generic[DepsT], ABC):
    """Agent class for generating responses using LLMs with tools."""

    ctx: Context[DepsT]
    """The context for the agent, such as the history of messages."""

    tools: Sequence[ToolDef] | None
    """The tools available to the agent, if any."""

    model: LLM
    """The default model the agent will use if not specified through context."""
