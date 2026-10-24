import contextlib
from collections.abc import AsyncIterator
from datetime import timedelta
from typing import cast

from mcp import ClientSession
from mcp.client.sse import sse_client as mcp_sse_client
from mcp.client.stdio import StdioServerParameters, stdio_client as mcp_stdio_client
from mcp.client.streamable_http import (
    streamable_http_client as mcp_streamable_http_client,
)
from mcp.types import (
    CallToolResult,
    PaginatedRequestParams,
    TextContent,
    Tool as MCPTool,
)

from ..tools import AsyncTool
from ..tools.tool_schema import ToolParameterSchema
from ..types import Jsonable


def _mcp_tool_parameters(mcp_tool: MCPTool) -> ToolParameterSchema:
    input_schema = mcp_tool.inputSchema
    parameters = ToolParameterSchema(
        properties=input_schema.get("properties", {}),
        required=input_schema.get("required", []),
        additionalProperties=input_schema.get("additionalProperties", False),
    )
    if "$defs" in input_schema:
        parameters.defs = input_schema["$defs"]
    return parameters


class MCPClient:
    """Mirascope wrapper around a MCP ClientSession.

    It provides a way to get MCP results that are pre-converted into Mirascope-friendly
    types.

    The underlying MCP ClientSession may be accessed by .session if needed.
    """

    def __init__(self, session: ClientSession) -> None:
        self._session = session

    @property
    def session(self) -> ClientSession:
        """Access the underlying MCP ClientSession if needed."""
        return self._session

    def _convert_mcp_tool_to_async_tool(self, mcp_tool: MCPTool) -> AsyncTool:
        """Convert an MCP Tool to a Mirascope AsyncTool.

        Args:
            mcp_tool: The MCP tool to convert.

        Returns:
            An `AsyncTool` that wraps the MCP tool.
        """

        # Create an async function that calls the MCP tool
        async def tool_fn(**kwargs: object) -> Jsonable:
            tool_result: CallToolResult = await self._session.call_tool(
                mcp_tool.name, kwargs
            )
            if tool_result.isError:
                # Surface the server-reported failure as a tool error, so the model is
                # told the call failed instead of reading the message as a result.
                raise ValueError(
                    "\n".join(
                        content.text
                        for content in tool_result.content
                        if isinstance(content, TextContent)
                    )
                    or f"MCP tool '{mcp_tool.name}' returned an error"
                )
            # Convert ContentBlock objects to JSON-serializable dicts
            # Cast to Jsonable since model_dump() returns dict[str, Any]
            return cast(
                Jsonable, [content.model_dump() for content in tool_result.content]
            )

        # Create the AsyncTool instance
        return AsyncTool(
            fn=tool_fn,
            name=mcp_tool.name,
            description=mcp_tool.description or mcp_tool.name,
            parameters=_mcp_tool_parameters(mcp_tool),
            strict=False,
        )

    async def list_tools(self) -> list[AsyncTool]:
        """List all tools available on the MCP server.

        Returns:
            A list of dynamically created `AsyncTool`s.

        Raises:
            ValueError: If the server returns a repeated pagination cursor.
        """
        tools: list[MCPTool] = []
        cursor: str | None = None
        seen_cursors: set[str] = set()
        while True:
            params = (
                PaginatedRequestParams(cursor=cursor) if cursor is not None else None
            )
            result = await self._session.list_tools(params=params)
            tools.extend(result.tools)
            cursor = result.nextCursor
            if cursor is None:
                return [self._convert_mcp_tool_to_async_tool(tool) for tool in tools]
            if cursor in seen_cursors:
                raise ValueError("MCP tools/list returned a repeated pagination cursor")
            seen_cursors.add(cursor)


@contextlib.asynccontextmanager
async def streamable_http_client(
    url: str,
) -> AsyncIterator[MCPClient]:  # pragma: no cover
    """Create a Mirascope MCPClient using StreamableHTTP."""
    # NOTE: If updating this function, unskip and manually run the TestTransportModes
    # tests in test_mcp_client.py. (Skipped because they are flaky)
    async with (
        mcp_streamable_http_client(url) as (read, write, _),
        ClientSession(read, write) as session,
    ):
        await session.initialize()
        yield MCPClient(session)


@contextlib.asynccontextmanager
async def stdio_client(
    server_parameters: StdioServerParameters,
    name: str | None = None,
) -> AsyncIterator[MCPClient]:
    """Create a Mirascope MCPClient using stdio."""
    async with (
        mcp_stdio_client(server_parameters) as (read, write),
        ClientSession(read, write) as session,
    ):
        await session.initialize()
        yield MCPClient(session)


@contextlib.asynccontextmanager
async def sse_client(
    url: str,
    read_timeout_seconds: timedelta | None = None,
) -> AsyncIterator[MCPClient]:  # pragma: no cover
    """Create a Mirascope MCPClient using sse."""
    # NOTE: If updating this function, unskip and manually run the TestTransportModes
    # tests in test_mcp_client.py. (Skipped because they are flaky)
    async with (
        mcp_sse_client(url) as (read, write),
        ClientSession(
            read, write, read_timeout_seconds=read_timeout_seconds
        ) as session,
    ):
        await session.initialize()
        yield MCPClient(session)
