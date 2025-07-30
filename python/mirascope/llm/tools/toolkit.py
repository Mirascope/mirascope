from collections.abc import Awaitable
from dataclasses import dataclass
from typing import Any, Generic, TypeVar, overload

from ..content import ToolCall, ToolOutput
from ..context import Context, DepsT
from ..types import Jsonable
from .context_tool import AsyncContextTool, ContextTool, ContextToolT
from .tool import AsyncTool, Tool, ToolT

ToolkitT = TypeVar(
    "ToolkitT",
    bound="Toolkit[Tool | AsyncTool]"
    | "ContextToolkit[Tool | AsyncTool | ContextTool | AsyncContextTool, Any]",
    covariant=True,
)

ToolReturnT = TypeVar("ToolReturnT", bound=Jsonable, covariant=True)
AsyncToolReturnT = TypeVar("AsyncToolReturnT", bound=Jsonable, covariant=True)


@dataclass(kw_only=True)
class Toolkit(Generic[ToolT]):
    tools: list[ToolT]

    def get(self, tool_call: ToolCall) -> ToolT:
        raise NotImplementedError()

    @overload
    def execute(
        self: "Toolkit[Tool[..., ToolReturnT]]", tool_call: ToolCall
    ) -> ToolOutput[ToolReturnT]: ...

    @overload
    def execute(
        self: "Toolkit[AsyncTool[..., AsyncToolReturnT]]", tool_call: ToolCall
    ) -> Awaitable[ToolOutput[AsyncToolReturnT]]: ...

    @overload
    def execute(
        self: "Toolkit[Tool[..., ToolReturnT] | AsyncTool[...,AsyncToolReturnT]]",
        tool_call: ToolCall,
    ) -> ToolOutput[ToolReturnT] | Awaitable[ToolOutput[AsyncToolReturnT]]: ...

    def execute(
        self, tool_call: ToolCall
    ) -> ToolOutput[Jsonable] | Awaitable[ToolOutput[Jsonable]] | None:
        raise NotImplementedError()


@dataclass(kw_only=True)
class ContextToolkit(Generic[ContextToolT, DepsT]):
    tools: list[ContextToolT]

    def get(self, tool_call: ToolCall) -> ContextToolT:
        raise NotImplementedError()

    @overload
    def execute(
        self: "ContextToolkit[Tool[..., ToolReturnT] | ContextTool[..., ToolReturnT, DepsT], DepsT]",
        ctx: Context[DepsT],
        tool_call: ToolCall,
    ) -> ToolOutput[ToolReturnT]: ...

    @overload
    def execute(
        self: "ContextToolkit[AsyncTool[..., AsyncToolReturnT] | AsyncContextTool[..., AsyncToolReturnT, DepsT], DepsT]",
        ctx: Context[DepsT],
        tool_call: ToolCall,
    ) -> Awaitable[ToolOutput[AsyncToolReturnT]]: ...

    @overload
    def execute(
        self: "ContextToolkit[Tool[..., ToolReturnT] | ContextTool[..., ToolReturnT, DepsT] | AsyncTool[..., AsyncToolReturnT] | AsyncContextTool[..., AsyncToolReturnT, DepsT], DepsT]",
        ctx: Context[DepsT],
        tool_call: ToolCall,
    ) -> ToolOutput[ToolReturnT] | Awaitable[ToolOutput[AsyncToolReturnT]]: ...

    def execute(
        self, ctx: Context[DepsT], tool_call: ToolCall
    ) -> ToolOutput[Jsonable] | Awaitable[ToolOutput[Jsonable]]:
        raise NotImplementedError()
