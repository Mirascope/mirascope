"""The `AgentContext class."""

from typing import Any

from ..core import BaseMessageParam


class AgentContext:
    """Base class for agent context objects."""

    messages: list[BaseMessageParam] = []

    def __init__(self, **data: Any) -> None:  # noqa: ANN401
        """Initializes an instance of `AgentContext.`"""
        for key, value in data.items():
            setattr(self, key, value)
