from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from ..content import ToolCall, ToolOutput
from ..context import Context, DepsT
from ..exceptions import ToolNotFoundError
from ..types import Jsonable
from .provider_tools import ProviderTool
from .tool_schema import ToolSchemaT
from .tools import AsyncContextTool, AsyncTool, ContextTool, Tool

ToolkitT = TypeVar(
    "ToolkitT",
    bound="Toolkit | AsyncToolkit | ContextToolkit[Any] | AsyncContextToolkit[Any]",
    covariant=True,
)


@dataclass
class BaseToolkit(Generic[ToolSchemaT]):
    """Base class for tool collections.

    Provides common functionality for managing collections of tools,
    including name validation and tool lookup.
    """

    tools: Sequence[ToolSchemaT | ProviderTool]
    """The tools included in the toolkit."""

    tools_dict: dict[str, ToolSchemaT]
    """A mapping from tool names to tools in the toolkit.

    This dict does not include any `ProviderTool`s, since they do not correspond
    to tool calls that your code executes.
    """

    provider_tools_dict: dict[str, ProviderTool]
    """A mapping from provider tool names to provider tools in the toolkit.

    Provider tools are capabilities built into the provider's API (like web search)
    that are executed server-side, not by your code.
    """

    def __init__(self, tools: Sequence[ToolSchemaT | ProviderTool] | None) -> None:
        """Initialize the toolkit with a collection of tools.

        Args:
            tools: Sequence of tools to include in the toolkit.

        Raises:
            ValueError: If multiple tools have the same name.
        """
        self.tools = tools or []
        self.tools_dict = {}
        self.provider_tools_dict = {}
        for tool in self.tools:
            if isinstance(tool, ProviderTool):
                if tool.name in self.provider_tools_dict:
                    raise ValueError(f"Multiple provider tools with name: {tool.name}")
                self.provider_tools_dict[tool.name] = tool
            else:
                if tool.name in self.tools_dict:
                    raise ValueError(f"Multiple tools with name: {tool.name}")
                self.tools_dict[tool.name] = tool

    def get(self, tool_call: ToolCall) -> ToolSchemaT:
        """Get a tool that can execute a specific tool call.

        Args:
            tool_call: The tool call containing the tool name to lookup.

        Returns:
            The tool whose name matches the tool call.

        Raises:
            ToolNotFoundError: If no tool with the given name exists.
        """
        tool = self.tools_dict.get(tool_call.name, None)
        if not tool:
            raise ToolNotFoundError(tool_call.name)
        return tool


class Toolkit(BaseToolkit[Tool]):
    """A collection of `Tool`s, with helpers for getting and executing specific tools."""

    def execute(self, tool_call: ToolCall) -> ToolOutput[Jsonable]:
        """Execute a `Tool` using the provided tool call.

        Args:
            tool_call: The tool call to execute.

        Returns:
            The output from executing the `Tool`.
        """
        try:
            tool = self.get(tool_call)
            return tool.execute(tool_call)
        except ToolNotFoundError as e:
            return ToolOutput(
                id=tool_call.id, result=str(e), error=e, name=tool_call.name
            )


class AsyncToolkit(BaseToolkit[AsyncTool]):
    """A collection of `AsyncTool`s, with helpers for getting and executing specific tools."""

    async def execute(self, tool_call: ToolCall) -> ToolOutput[Jsonable]:
        """Execute an `AsyncTool` using the provided tool call.

        Args:
            tool_call: The tool call to execute.

        Returns:
            The output from executing the `AsyncTool`.
        """
        try:
            tool = self.get(tool_call)
            return await tool.execute(tool_call)
        except ToolNotFoundError as e:
            return ToolOutput(
                id=tool_call.id, result=str(e), error=e, name=tool_call.name
            )


class ContextToolkit(BaseToolkit[Tool | ContextTool[DepsT]], Generic[DepsT]):
    """A collection of `ContextTool`s, with helpers for getting and executing specific tools."""

    def execute(self, ctx: Context[DepsT], tool_call: ToolCall) -> ToolOutput[Jsonable]:
        """Execute a `ContextTool` using the provided tool call.

        Args:
            ctx: The context containing dependencies that match the tool.
            tool_call: The tool call to execute.

        Returns:
            The output from executing the `ContextTool`.
        """
        try:
            tool = self.get(tool_call)
            if isinstance(tool, ContextTool):
                return tool.execute(ctx, tool_call)
            else:
                return tool.execute(tool_call)
        except ToolNotFoundError as e:
            return ToolOutput(
                id=tool_call.id, result=str(e), error=e, name=tool_call.name
            )


class AsyncContextToolkit(
    BaseToolkit[AsyncTool | AsyncContextTool[DepsT]], Generic[DepsT]
):
    """A collection of `AsyncContextTool`s, with helpers for getting and executing specific tools."""

    async def execute(
        self, ctx: Context[DepsT], tool_call: ToolCall
    ) -> ToolOutput[Jsonable]:
        """Execute an `AsyncContextTool` using the provided tool call.

        Args:
            ctx: The context containing dependencies that match the tool.
            tool_call: The tool call to execute.

        Returns:
            The output from executing the `AsyncContextTool`.
        """
        try:
            tool = self.get(tool_call)
            if isinstance(tool, AsyncContextTool):
                return await tool.execute(ctx, tool_call)
            else:
                return await tool.execute(tool_call)
        except ToolNotFoundError as e:
            return ToolOutput(
                id=tool_call.id, result=str(e), error=e, name=tool_call.name
            )
