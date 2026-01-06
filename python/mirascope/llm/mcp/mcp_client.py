import contextlib
from collections.abc import AsyncIterator
from datetime import timedelta

from mcp import ClientSession
from mcp.client.sse import sse_client as mcp_sse_client
from mcp.client.stdio import StdioServerParameters, stdio_client as mcp_stdio_client
from mcp.client.streamable_http import (
    streamablehttp_client as mcp_streamablehttp_client,
)

from ..tools import AsyncTool


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

    async def list_tools(self) -> list[AsyncTool]:
        """List all tools available on the MCP server.

        Returns:
            A list of dynamically created `llm.Tool`s.
        """
        raise NotImplementedError()


@contextlib.asynccontextmanager
async def streamablehttp_client(
    url: str,
) -> AsyncIterator[MCPClient]:
    """Create a Mirascope MCPClient using StreamableHTTP."""
    async with (
        mcp_streamablehttp_client(url) as (read, write, _),
        ClientSession(read, write) as session,
    ):
        await session.initialize()
        # TODO: Add e2e test with a real HTTP server
        yield MCPClient(session)  # pragma: no cover


@contextlib.asynccontextmanager
async def stdio_client(
    server_parameters: StdioServerParameters,
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
) -> AsyncIterator[MCPClient]:
    """Create a Mirascope MCPClient using sse."""
    async with (
        mcp_sse_client(url) as (read, write),
        ClientSession(
            read, write, read_timeout_seconds=read_timeout_seconds
        ) as session,
    ):
        # TODO: Add e2e test with a real sse client
        await session.initialize()  # pragma: no cover
        yield MCPClient(session)  # pragma: no cover
