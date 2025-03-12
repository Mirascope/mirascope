"""The `AgentResponse class."""

from typing import Generic, TypeVar

from ._response_metaclass import _ResponseMetaclass
from .agent_context import AgentContext
from .call_response import CallResponse

_AgentContextT = TypeVar("_AgentContextT", bound=AgentContext)


class AgentResponse(
    CallResponse,
    Generic[_AgentContextT],
    metaclass=_ResponseMetaclass,
):
    """A response from an `llm.agent` call.

    This class is a `CallResponse` with additional attributes for tracking the context.

    Attributes:
        previous_context: The context as it was at the beginning of the agent's execution.
            This allows for comparing the state before and after execution.
    """

    previous_context: _AgentContextT
