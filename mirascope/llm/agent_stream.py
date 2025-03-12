"""The `AgentStream` Class."""

from typing import Generic, TypeVar

from .agent_context import AgentContext
from .stream import Stream

_AgentContextT = TypeVar("_AgentContextT", bound=AgentContext)


class AgentStream(Stream, Generic[_AgentContextT]):
    """A stream from an `llm.agent` call.

    This class is a `Stream` with additional attributes for tracking the context.

    Attributes:
        previous_context: The context as it was at the beginning of the agent's execution.
            This allows for comparing the state before and after execution.
    """

    previous_context: _AgentContextT
