"""ContextTool interface for LLM tools that need access to the context."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Concatenate, Generic, TypeVar

from ..contexts import Context
from ..types import Jsonable

R = TypeVar("R", bound=Jsonable)


@dataclass
class ContextTool(Generic[R]):
    """ContextTool interface for LLM tools that need access to the context.

    This interface is used for tools that require access to the context of the LLM
    call. It provides a method to set the context and a method to get the context.
    """

    fn: Callable[Concatenate[Context, ...], R]
    """The function that defines the tool being calledm, which takes a Context as the first argument."""

    name: str
    """The name of the tool being called."""

    args: dict[str, Jsonable]
    """The arguments provided by the LLM for this tool call."""

    id: str
    """Unique identifier for this tool call."""

    def call(self, context: Context) -> R:
        """Execute the tool with the context provided by the LLM.

        Args:
            context: The context to be passed to the tool.

        Returns:
            The result of executing the tool with the provided context.
        """
        raise NotImplementedError()
