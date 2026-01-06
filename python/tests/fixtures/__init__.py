"""Test fixtures for Mirascope tests."""

from __future__ import annotations

import asyncio
import socket
import subprocess
import sys
from collections.abc import AsyncGenerator
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Literal, overload

from mcp.client.stdio import StdioServerParameters

__all__ = ["mcp_server"]


@overload
def mcp_server(
    transport: Literal["stdio"],
) -> AbstractAsyncContextManager[StdioServerParameters]: ...


@overload
def mcp_server(
    transport: Literal["http", "sse"],
) -> AbstractAsyncContextManager[str]: ...


@asynccontextmanager
async def mcp_server(
    transport: Literal["http", "sse", "stdio"],
) -> AsyncGenerator[str | StdioServerParameters, None]:
    """Start an MCP test server with the specified transport.

    Args:
        transport: The transport type to use (http, sse, or stdio)

    Yields:
        For http/sse: The URL to connect to the server
        For stdio: StdioServerParameters to connect to the server
    """
    if transport == "stdio":
        # Stdio doesn't need a subprocess - it's handled by the client
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "tests.fixtures.example_mcp_server"],
            env=None,
        )
        yield server_params
        return

    # Find an available port for http/sse
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
        for _ in range(20):
            try:
                _, writer = await asyncio.open_connection("127.0.0.1", port)
                writer.close()
                await writer.wait_closed()
                break
            except (ConnectionRefusedError, OSError):
                await asyncio.sleep(0.1)

        # Return appropriate URL based on transport
        if transport == "sse":
            yield f"http://127.0.0.1:{port}/sse"
        else:  # http
            yield f"http://127.0.0.1:{port}/mcp"
    finally:
        proc.terminate()
        proc.wait(timeout=2)
