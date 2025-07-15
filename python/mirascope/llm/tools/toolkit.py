from collections.abc import Awaitable
from dataclasses import dataclass
from typing import Generic, overload

from ..content import ToolCall, ToolOutput
from ..types import Jsonable
from .async_tool import AsyncTool
from .tool import Tool
from .tool_typevars import AT, T, ToolT


@dataclass(kw_only=True)
class Toolkit(Generic[ToolT]):
    tools: list[ToolT]

    def get(self, tool_call: ToolCall) -> ToolT:
        raise NotImplementedError()

    @overload
    def call(self: "Toolkit[Tool[..., T]]", tool_call: ToolCall) -> ToolOutput[T]: ...
    @overload
    def call(
        self: "Toolkit[AsyncTool[..., AT]]", tool_call: ToolCall
    ) -> Awaitable[ToolOutput[AT]]: ...
    @overload
    def call(
        self: "Toolkit[Tool[..., T] | AsyncTool[...,AT]]", tool_call: ToolCall
    ) -> ToolOutput[T] | Awaitable[ToolOutput[AT]]: ...

    def call(
        self, tool_call: ToolCall
    ) -> ToolOutput[Jsonable] | Awaitable[ToolOutput[Jsonable]] | None:
        raise NotImplementedError()
