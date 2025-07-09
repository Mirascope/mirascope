"""The `BaseStructuredAgent` class for structured LLM agents."""

from abc import ABC
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic

from ..context import Context
from ..models import LLM
from ..tools import ToolDef
from ..types import DepsT, FormatT


@dataclass
class BaseStructuredAgent(Generic[DepsT, FormatT], ABC):
    """Structured agent class for generating structured responses using LLMs with tools."""

    ctx: Context[DepsT]
    """The context for the agent, such as the history of messages."""

    response_format: type[FormatT] | None
    """The response format for the agent, if any."""

    tools: Sequence[ToolDef] | None
    """The tools available to the agent, if any."""

    model: LLM
    """The default model the agent will use if not specified through context."""
