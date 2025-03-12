"""The `AgentResponse` Class."""

from __future__ import annotations

from typing import Generic, TypeVar

from ...llm._response_metaclass import _ResponseMetaclass
from ...llm.call_response import CallResponse
from .agent_context import AgentContext

_DepsT = TypeVar("_DepsT")


class AgentResponse(
    CallResponse,
    Generic[_DepsT],
    metaclass=_ResponseMetaclass,
):
    """A response from an `llm.agent` call.

    This class is a `CallResponse` with additional attributes for tracking the context.

    Attributes:
        previous_context: The context as it was at the beginning of the agent's execution.
            This allows for comparing the state before and after execution.
    """

    previous_context: AgentContext[_DepsT]
