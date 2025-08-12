"""The `Tool` class for defining tools that LLMs can request be called."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TypeVar

from ..content import ToolCall, ToolOutput
from ..types import Jsonable, JsonableCovariantT, P
from .tool_schema import ToolSchema

ToolT = TypeVar(
    "ToolT",
    bound="Tool[..., Jsonable] | AsyncTool[..., Jsonable]",
    covariant=True,
)


@dataclass
class Tool(ToolSchema[P, JsonableCovariantT]):
    """A tool that can be used by LLMs.

    A `Tool` represents a function that can be called by an LLM during a call.
    It includes metadata like name, description, and parameter schema.

    This class is not instantiated directly but created by the `@tool()` decorator.
    """

    fn: Callable[P, JsonableCovariantT]
    """The function that implements the tool's functionality."""

    @classmethod
    def from_function(
        cls, fn: Callable[P, JsonableCovariantT], *, strict: bool = False
    ) -> Tool[P, JsonableCovariantT]:
        """Create a `Tool` from a function."""
        schema = ToolSchema.create_schema(fn, strict=strict)
        return cls(
            fn=fn,
            name=schema.name,
            description=schema.description,
            parameters=schema.parameters,
            strict=schema.strict,
        )

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> JsonableCovariantT:
        """Call the underlying function directly."""
        return self.fn(*args, **kwargs)

    def execute(self, tool_call: ToolCall) -> ToolOutput[JsonableCovariantT]:
        """Execute the tool using an LLM-provided `ToolCall`."""
        result = self.fn(**tool_call.args)  # type: ignore[reportCallIssue]
        return ToolOutput(id=tool_call.id, value=result)

    def __hash__(self) -> int:
        """Hash based on schema fields only, ignoring the fn field."""
        return super().__hash__()


@dataclass
class AsyncTool(ToolSchema[P, JsonableCovariantT]):
    """An async tool that can be used by LLMs.

    An `AsyncTool` represents an async function that can be called by an LLM during a call.
    It includes metadata like name, description, and parameter schema.

    This class is not instantiated directly but created by the `@tool()` decorator.
    """

    fn: Callable[P, Awaitable[JsonableCovariantT]]
    """The async function that implements the tool's functionality."""

    @classmethod
    def from_function(
        cls, fn: Callable[P, Awaitable[JsonableCovariantT]], *, strict: bool = False
    ) -> AsyncTool[P, JsonableCovariantT]:
        """Create an `AsyncTool` from a function."""
        schema = ToolSchema.create_schema(fn, strict=strict)
        return cls(
            fn=fn,
            name=schema.name,
            description=schema.description,
            parameters=schema.parameters,
            strict=schema.strict,
        )

    def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Awaitable[JsonableCovariantT]:
        """Call the underlying async function directly."""
        return self.fn(*args, **kwargs)

    async def execute(self, tool_call: ToolCall) -> ToolOutput[JsonableCovariantT]:
        """Execute the async tool using an LLM-provided `ToolCall`."""
        result = await self.fn(**tool_call.args)  # type: ignore[reportCallIssue]
        return ToolOutput(id=tool_call.id, value=result)

    def __hash__(self) -> int:
        """Hash based on schema fields only, ignoring the fn field."""
        return super().__hash__()
