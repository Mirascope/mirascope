"""Example MCP server for testing purposes.

This server provides various tools for testing MCP client functionality
across unit, integration, and e2e tests.
"""

import argparse
import asyncio
import socket
import subprocess
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Literal

from fastmcp import FastMCP
from mcp.client.stdio import StdioServerParameters
from pydantic import BaseModel, Field

from mirascope import llm


@asynccontextmanager
async def example_mcp_client(
    transport: Literal["http", "sse", "stdio"],
) -> "AsyncGenerator[llm.mcp.MCPClient, None]":
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
            args=["-m", "tests.llm.mcp.example_mcp_client"],
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
            "tests.llm.mcp.example_mcp_server",
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


test_server = FastMCP("mirascope-test-server")


# Define models after creating server but before using in tool decorators
class ComputerInfo(BaseModel):
    """Information about Deep Thought computer."""

    name: str = Field(description="The name of the computer")
    years_computed: int = Field(description="How many years it took to compute")


class UltimateAnswer(BaseModel):
    """The answer to life, the universe, and everything."""

    answer: int = Field(description="The numerical answer")
    question: str = Field(description="The question that was asked")
    computed_by: ComputerInfo = Field(description="Information about the computer")


@test_server.tool()
def greet(name: str) -> str:
    """Greet a user with very special welcome.

    Args:
        name: The name of the person to greet

    Returns:
        A personalized welcome message
    """
    return f"Welcome to Zombo.com, {name}"


@test_server.tool()
def answer_ultimate_question() -> UltimateAnswer:
    """Answer the ultimate question of life, the universe, and everything.

    Returns:
        A structured answer with metadata about the computation
    """
    return UltimateAnswer(
        answer=42,
        question="What is the answer to life, the universe, and everything?",
        computed_by=ComputerInfo(name="Deep Thought", years_computed=7_500_000),
    )


@test_server.tool()
def process_answer(answer_data: UltimateAnswer) -> str:
    """Process and format an ultimate answer.

    This tool demonstrates complex schema with $defs by accepting
    a nested Pydantic model as input.

    Args:
        answer_data: The answer data to process

    Returns:
        A formatted string describing the answer
    """
    return (
        f"The answer {answer_data.answer} to '{answer_data.question}' "
        f"was computed by {answer_data.computed_by.name} "
        f"over {answer_data.computed_by.years_computed:,} years"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the example MCP test server")
    parser.add_argument(
        "--transport",
        default="stdio",
        choices=["http", "sse", "stdio"],
        help="Transport protocol to use",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the server on (for http/sse)",
    )
    args = parser.parse_args()

    if args.transport == "stdio":
        test_server.run()
    else:
        test_server.run(transport=args.transport, host="127.0.0.1", port=args.port)
