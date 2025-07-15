from collections.abc import Awaitable
from dataclasses import dataclass
from typing import Generic, overload

from ..content import ToolCall, ToolOutput
from ..context import Context, DepsT
from ..types import Jsonable
from .async_context_tool import AsyncContextTool
from .async_tool import AsyncTool
from .context_tool import ContextTool
from .tool import Tool
from .tool_typevars import AT, ContextToolT, T


@dataclass(kw_only=True)
class ContextToolkit(Generic[ContextToolT, DepsT]):
    tools: list[ContextToolT]

    def get(self, tool_call: ToolCall) -> ContextToolT:
        raise NotImplementedError()

    @overload
    def call(
        self: "ContextToolkit[Tool[..., T] | ContextTool[..., T, DepsT], DepsT]",
        ctx: Context[DepsT],
        tool_call: ToolCall,
    ) -> ToolOutput[T]: ...
    @overload
    def call(
        self: "ContextToolkit[AsyncTool[..., AT] | AsyncContextTool[..., AT, DepsT], DepsT]",
        ctx: Context[DepsT],
        tool_call: ToolCall,
    ) -> Awaitable[ToolOutput[AT]]: ...
    @overload
    def call(
        self: "ContextToolkit[Tool[..., T] | ContextTool[..., T, DepsT] | AsyncTool[..., AT] | AsyncContextTool[..., AT, DepsT], DepsT]",
        ctx: Context[DepsT],
        tool_call: ToolCall,
    ) -> ToolOutput[T] | Awaitable[ToolOutput[AT]]: ...

    def call(
        self, ctx: Context[DepsT], tool_call: ToolCall
    ) -> ToolOutput[Jsonable] | Awaitable[ToolOutput[Jsonable]]:
        raise NotImplementedError()
