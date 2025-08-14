from collections.abc import Awaitable
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from ..content import ToolCall, ToolOutput
from ..context import Context, DepsT
from ..types import Jsonable
from .context_tool import AsyncContextTool, ContextTool
from .tool import AsyncTool, Tool

ToolkitT = TypeVar(
    "ToolkitT",
    bound="Toolkit | AsyncToolkit | ContextToolkit[Any] | AsyncContextToolkit[Any]",
    covariant=True,
)


@dataclass(kw_only=True)
class Toolkit:
    tools: list[Tool]

    def get(self, tool_call: ToolCall) -> Tool:
        raise NotImplementedError()

    def execute(self, tool_call: ToolCall) -> ToolOutput[Jsonable]:
        raise NotImplementedError()


@dataclass(kw_only=True)
class AsyncToolkit:
    tools: list[AsyncTool]

    def get(self, tool_call: ToolCall) -> AsyncTool:
        raise NotImplementedError()

    def execute(self, tool_call: ToolCall) -> Awaitable[ToolOutput[Jsonable]]:
        raise NotImplementedError()


@dataclass(kw_only=True)
class ContextToolkit(Generic[DepsT]):
    tools: list[Tool | ContextTool[DepsT, ...]]

    def get(self, tool_call: ToolCall) -> Tool | ContextTool[DepsT, ...]:
        raise NotImplementedError()

    def execute(self, ctx: Context[DepsT], tool_call: ToolCall) -> ToolOutput[Jsonable]:
        raise NotImplementedError()


@dataclass(kw_only=True)
class AsyncContextToolkit(Generic[DepsT]):
    tools: list[AsyncTool | AsyncContextTool[DepsT, ...]]

    def get(self, tool_call: ToolCall) -> AsyncTool | AsyncContextTool[DepsT, ...]:
        raise NotImplementedError()

    def execute(
        self, ctx: Context[DepsT], tool_call: ToolCall
    ) -> Awaitable[ToolOutput[Jsonable]]:
        raise NotImplementedError()
