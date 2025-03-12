"""The `AgentStream` Class."""

from typing import Generic, TypeVar

from ...llm.stream import Stream
from .agent_context import AgentContext

_DepsT = TypeVar("_DepsT")


class AgentStream(Stream, Generic[_DepsT]):
    """A stream from an `llm.agent` call.

    This class is a `Stream` with additional attributes for tracking the context.

    Attributes:
        previous_context: The context as it was at the beginning of the agent's execution.
            This allows for comparing the state before and after execution.
    """

    previous_context: AgentContext[_DepsT]
