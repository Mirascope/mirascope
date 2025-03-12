"""The `AgentContext class."""

from typing import Any, Generic, TypeVar

from ..core import BaseMessageParam

_DepsTypeT = TypeVar("_DepsTypeT")


class AgentContext(Generic[_DepsTypeT]):
    """Base class for agent context objects."""

    deps: _DepsTypeT
    messages: list[BaseMessageParam] = []

    def __init__(self, **data: Any) -> None:  # noqa: ANN401
        """Initializes an instance of `AgentContext.`"""
        for key, value in data.items():
            setattr(self, key, value)
