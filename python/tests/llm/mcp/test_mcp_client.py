"""Tests for Mirascope MCP client functionality."""

from __future__ import annotations

import pytest

from mirascope import llm
from tests.fixtures import mcp_server


class TestMCPClient:
    """Integration tests for MCPClient basic functionality."""

    @pytest.mark.asyncio
    async def test_mcp_session(self) -> None:
        """Test that list_tools raises NotImplementedError."""
        async with mcp_server("stdio") as client:
            assert client.session is not None

    @pytest.mark.asyncio
    async def test_list_tools_not_implemented(self) -> None:
        """Test that list_tools raises NotImplementedError."""
        async with mcp_server("stdio") as client:
            with pytest.raises(NotImplementedError):
                await client.list_tools()


@pytest.mark.skip("Flaky — run manually if changing transport code")
class TestTransportModes:
    """Tests for different MCP transport modes (SSE, HTTP).

    These tests verify that each transport mode can successfully establish
    a connection to an MCP server.

    Note: The stdio approach is the most reliable and is used in other testing, but we
    include it here for completeness.

    The sse and http connections run into teardown/flakiness issues.
    """

    @pytest.mark.asyncio
    async def test_stdio_transport(self) -> None:
        """Test that stdio transport successfully connects to MCP server."""
        async with mcp_server("stdio") as client:
            assert isinstance(client, llm.mcp.MCPClient)
            assert client.session is not None

    @pytest.mark.asyncio
    async def test_sse_transport(self) -> None:
        """Test that SSE transport successfully connects to MCP server."""
        async with mcp_server("sse") as client:
            assert isinstance(client, llm.mcp.MCPClient)
            assert client.session is not None

    @pytest.mark.asyncio
    async def test_http_transport(self) -> None:
        """Test that HTTP transport successfully connects to MCP server."""
        async with mcp_server("http") as client:
            assert isinstance(client, llm.mcp.MCPClient)
            assert client.session is not None
