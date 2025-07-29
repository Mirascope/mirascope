import contextlib
from collections.abc import AsyncIterator, Callable
from datetime import timedelta

import httpx
from mcp import ClientSession
from mcp.client.session import ListRootsFnT, SamplingFnT
from mcp.client.sse import sse_client as mcp_sse_client
from mcp.client.stdio import StdioServerParameters
from mcp.client.streamable_http import (
    streamablehttp_client as mcp_streamablehttp_client,
)
from mcp.shared._httpx_utils import McpHttpClientFactory

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
    headers: dict[str, str] | None = None,
    timeout: float | timedelta | None = None,
    sse_read_timeout: float | timedelta | None = None,
    terminate_on_close: bool = True,
    httpx_client_factory: McpHttpClientFactory | None = None,
    auth: httpx.Auth | None = None,
) -> AsyncIterator[MCPClient]:
    """Create a Mirascope MCPClient using StreamableHTTP."""
    kwargs = {}
    if headers is not None:
        kwargs["headers"] = headers
    if timeout is not None:
        kwargs["timeout"] = timeout
    if sse_read_timeout is not None:
        kwargs["sse_read_timeout"] = sse_read_timeout
    if httpx_client_factory is not None:
        kwargs["httpx_client_factory"] = httpx_client_factory
    if auth is not None:
        kwargs["auth"] = auth

    async with (
        mcp_streamablehttp_client(
            url,
            terminate_on_close=terminate_on_close,
            **kwargs,
        ) as (read, write, get_session_id),
        ClientSession(
            read,
            write,
        ) as session,
    ):
        await session.initialize()
        yield MCPClient(session)


@contextlib.asynccontextmanager
async def stdio_client(
    server_parameters: StdioServerParameters,
    read_stream_exception_handler: Callable[[Exception], None] | None = None,
) -> AsyncIterator[MCPClient]:
    """Create a Mirascope MCPClient using stdio."""

    async with (
        ClientSession(None, None) as session,  # pyright: ignore [reportArgumentType]
    ):
        raise NotImplementedError()
        await session.initialize()
        yield MCPClient(session)


@contextlib.asynccontextmanager
async def sse_client(
    url: str,
    list_roots_callback: ListRootsFnT | None = None,
    read_timeout_seconds: timedelta | None = None,
    sampling_callback: SamplingFnT | None = None,
    session: ClientSession | None = None,
) -> AsyncIterator[MCPClient]:
    """Create a Mirascope MCPClient using sse."""

    async with (
        mcp_sse_client(url) as (read, write),
        ClientSession(
            read,
            write,
            read_timeout_seconds=read_timeout_seconds,
            sampling_callback=sampling_callback,
            list_roots_callback=list_roots_callback,
        ) as session,
    ):
        await session.initialize()
        yield MCPClient(session)
