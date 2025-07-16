from collections.abc import Awaitable
from dataclasses import dataclass
from typing import Generic, overload

from ..content import ToolCall, ToolOutput
from ..types import Jsonable
from .async_tool import AsyncTool
from .tool import Tool
from .tool_typevars import AsyncToolReturnT, ToolReturnT, ToolT


@dataclass(kw_only=True)
class Toolkit(Generic[ToolT]):
    tools: list[ToolT]

    def get(self, tool_call: ToolCall) -> ToolT:
        raise NotImplementedError()

    @overload
    def call(
        self: "Toolkit[Tool[..., ToolReturnT]]", tool_call: ToolCall
    ) -> ToolOutput[ToolReturnT]: ...
    @overload
    def call(
        self: "Toolkit[AsyncTool[..., AsyncToolReturnT]]", tool_call: ToolCall
    ) -> Awaitable[ToolOutput[AsyncToolReturnT]]: ...
    @overload
    def call(
        self: "Toolkit[Tool[..., ToolReturnT] | AsyncTool[...,AsyncToolReturnT]]",
        tool_call: ToolCall,
    ) -> ToolOutput[ToolReturnT] | Awaitable[ToolOutput[AsyncToolReturnT]]: ...

    def call(
        self, tool_call: ToolCall
    ) -> ToolOutput[Jsonable] | Awaitable[ToolOutput[Jsonable]] | None:
        raise NotImplementedError()
