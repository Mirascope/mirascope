"""The `BaseAgent` class for LLM agents."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic

from typing_extensions import TypeVar

from ..contexts import Context
from ..models import LLM
from ..tools import ToolDef

DepsT = TypeVar("DepsT", default=None)


@dataclass
class BaseAgent(Generic[DepsT]):
    """Agent class for generating responses using LLMs with tools."""

    ctx: Context[DepsT]
    """The context for the agent, such as the history of messages."""

    tools: Sequence[ToolDef] | None
    """The tools available to the agent, if any."""

    model: LLM
    """The default model the agent will use if not specified through context."""
