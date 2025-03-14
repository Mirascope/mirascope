"""The `AgentContext class."""

from typing import TypeVar

from ...core import BaseMessageParam
from ..graphs.finite_state_machine import RunContext

_DepsTypeT = TypeVar("_DepsTypeT")


class AgentContext(RunContext[_DepsTypeT]):
    """Base class for agent context objects."""

    messages: list[BaseMessageParam] = []
