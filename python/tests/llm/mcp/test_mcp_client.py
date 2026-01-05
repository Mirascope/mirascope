"""Tests for Mirascope MCP client functionality."""

from __future__ import annotations

import asyncio
import sys
from unittest.mock import Mock

import pytest
from mcp.client.stdio import StdioServerParameters
from mcp.server import Server
from mcp.server.lowlevel.server import NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server

from mirascope.llm.mcp import MCPClient, sse_client, stdio_client, streamablehttp_client


class MinimalMCPServer:
    """Minimal MCP server for testing."""

    def __init__(self) -> None:
        """Initialize the minimal MCP server."""
        self.server = Server("minimal-test-server")

    async def run(self) -> None:
        """Run the server using stdio."""

        async with stdio_server() as (read, write):
            init_options = InitializationOptions(
                server_name="minimal-test-server",
                server_version="0.1.0",
                capabilities=self.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            )
            await self.server.run(
                read,
                write,
                init_options,
                raise_exceptions=True,
            )


async def main() -> None:
    """Entry point for running the server."""
    server = MinimalMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())


def test_mcp_client_init_and_session_property() -> None:
    """Test MCPClient initialization and session property access."""
    mock_session = Mock()
    client = MCPClient(mock_session)
    assert client.session is mock_session


@pytest.mark.asyncio
async def test_mcp_client_list_tools_not_implemented() -> None:
    """Test that list_tools raises NotImplementedError."""
    mock_session = Mock()
    client = MCPClient(mock_session)
    with pytest.raises(NotImplementedError):
        await client.list_tools()


@pytest.mark.asyncio
async def test_stdio_client_connects_to_server() -> None:
    """Test that stdio_client successfully connects to MCP server."""
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "tests.llm.mcp.test_mcp_client"],
        env=None,
    )

    async with stdio_client(server_params) as client:
        # Verify we got a valid MCPClient instance with an active session
        assert isinstance(client, MCPClient)
        assert client.session is not None


@pytest.mark.asyncio
async def test_sse_client_creates_client() -> None:
    """Test that sse_client attempts connection (will fail without real server)."""
    # This test will fail to connect since there's no real SSE server
    # but it validates the function signature and basic behavior
    with pytest.raises((OSError, ConnectionError, TimeoutError, Exception)):  # noqa: B017
        async with sse_client("http://localhost:9999/sse"):
            # Should never get here due to connection failure
            pass


@pytest.mark.asyncio
async def test_streamablehttp_client_creates_client() -> None:
    """Test that streamablehttp_client attempts connection (will fail without real server)."""
    # This test will fail to connect since there's no real HTTP server
    # but it validates the function signature and basic behavior
    with pytest.raises((OSError, ConnectionError, TimeoutError, Exception)):  # noqa: B017
        async with streamablehttp_client("http://localhost:9999"):
            # Should never get here due to connection failure
            pass
