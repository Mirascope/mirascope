"""Test fixtures for Mirascope tests."""

from __future__ import annotations

import asyncio
import socket
import subprocess
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Literal

from mcp.client.stdio import StdioServerParameters

from mirascope import llm

__all__ = ["mcp_server"]


@asynccontextmanager
async def mcp_server(
    transport: Literal["http", "sse", "stdio"],
) -> AsyncGenerator[llm.mcp.MCPClient, None]:
    """Start an MCP test server and return a connected MCPClient.

    Args:
        transport: The transport type to use (http, sse, or stdio)
        name: Optional name for the MCP client

    Yields:
        A connected MCPClient instance

    NOTE: This is reliable in "stdio" mode, but KNOWN FLAKEY in sse and http.
    The sse and http modes should only be used in skipped tests, that are unskipped
    when testing changes to the transport-specific connection code (very rare).
    """

    if transport == "stdio":
        # Stdio doesn't need a subprocess - it's handled by the client
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "tests.fixtures.example_mcp_server"],
            env=None,
        )
        async with llm.mcp.stdio_client(server_params) as client:
            yield client
        return

    # Find an available port for http/sse
    # TODO: Avoid socket-closed-and-grabbed race condition if we want to fix flakiness
    with socket.socket() as s:
        s.bind(("", 0))
        port = s.getsockname()[1]

    # Start server in subprocess for proper isolation
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "tests.fixtures.example_mcp_server",
            "--transport",
            transport,
            "--port",
            str(port),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        # Wait for server to be ready
        # TODO: Improve error handling here if we want to address flakiness
        for _ in range(20):
            try:
                _, writer = await asyncio.open_connection("127.0.0.1", port)
                writer.close()
                await writer.wait_closed()
                break
            except (ConnectionRefusedError, OSError):
                await asyncio.sleep(0.1)

        # Get appropriate URL and client based on transport
        if transport == "sse":
            url = f"http://127.0.0.1:{port}/sse"
            async with llm.mcp.sse_client(url) as client:
                yield client
        else:  # http
            url = f"http://127.0.0.1:{port}/mcp"
            async with llm.mcp.streamable_http_client(url) as client:
                yield client
    finally:
        proc.terminate()
        proc.wait(timeout=2)
