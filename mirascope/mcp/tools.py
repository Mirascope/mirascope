"""The `MCPTool` class for easy tool usage with MCPTool LLM calls.

usage docs: learn/tools.md

DEPRECATED: The MCPTool class is deprecated and will be removed in a future version.
Mirascope will only implement the client-side of MCP in the future, allowing it to connect to any
MCP server implementation, even if not built with Mirascope.
"""

from __future__ import annotations

import warnings
from typing import Any

from pydantic import BaseModel
from pydantic.json_schema import SkipJsonSchema
from typing_extensions import Required, TypedDict

from mirascope.core import BaseTool
from mirascope.core.base import ToolConfig


class ToolParam(TypedDict, total=False):
    input_schema: Required[dict[str, Any]]
    name: Required[str]
    description: str


class ToolUseBlock(BaseModel):
    id: str
    input: dict[str, Any]
    name: str


class MCPToolToolConfig(ToolConfig, total=False):
    """A tool configuration for mcp-specific features."""


class MCPTool(BaseTool):
    """A class for defining tools for MCP LLM calls.

    DEPRECATED: The MCPTool class is deprecated and will be removed in a future version.
    Mirascope will only implement the client-side of MCP in the future.

    Example:

    ```python
    import asyncio

    from mirascope.mcp import MCPServer

    app = MCPServer("book-recommend")


    @app.tool()
    async def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"

    asyncio.run(app.run())
    ```
    """

    __provider__ = "mcp"
    __tool_config_type__ = MCPToolToolConfig

    tool_call: SkipJsonSchema[ToolUseBlock]

    @classmethod
    def tool_schema(cls) -> ToolParam:
        """Constructs a `ToolParam` tool schema from the `BaseModel` schema defined.

        Example:
        ```python
        from mirascope.mcp import MCPTool


        def format_book(title: str, author: str) -> str:
            return f"{title} by {author}"


        tool_type = MCPTool.type_from_fn(format_book)
        print(tool_type.tool_schema())  # prints the MCP-specific tool schema
        ```
        """
        # Show deprecation warning
        warnings.warn(
            "The MCPTool class is deprecated and will be removed in a future version. "
            "Mirascope will only implement the client-side of MCP in the future. "
            "We recommend using the official MCP SDK (e.g. `FastMCP`) for server-side implementations.",
            DeprecationWarning,
            stacklevel=2,
        )
        kwargs = {
            "input_schema": cls.model_json_schema(),
            "name": cls._name(),
            "description": cls._description(),
        }
        return ToolParam(**kwargs)

    @classmethod
    def from_tool_call(cls, tool_call: ToolUseBlock) -> MCPTool:
        """Constructs an `MCPTool` instance from a `tool_call`.

        Args:
            tool_call: The MCP tool call from which to construct this tool
                instance.
        """
        model_json = {"tool_call": tool_call}
        model_json |= tool_call.input
        return cls.model_validate(model_json)
