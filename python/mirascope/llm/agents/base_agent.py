"""The `BaseAgent` class for LLM agents."""

from abc import ABC
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic

from ..context import Context, DepsT
from ..models import LLM
from ..response_formatting import FormatT
from ..tools import ToolDef


@dataclass
class BaseAgent(Generic[DepsT, FormatT], ABC):
    """Agent class for generating responses using LLMs with tools."""

    ctx: Context[DepsT]
    """The context for the agent, such as the history of messages."""

    tools: Sequence[ToolDef] | None
    """The tools available to the agent, if any."""

    response_format: type[FormatT] | None
    """The response format for the generated response."""

    model: LLM
    """The default model the agent will use if not specified through context."""
