"""Tests for Mirascope MCP client functionality."""

from __future__ import annotations

import pytest
from inline_snapshot import snapshot

from mirascope import llm
from mirascope.llm.mcp import MCPClient, sse_client, stdio_client, streamablehttp_client
from tests.fixtures import mcp_server


class TestMCPClient:
    """Integration tests for MCPClient basic functionality."""

    @pytest.mark.asyncio
    async def test_list_tools(self) -> None:
        """Test that list_tools returns Mirascope AsyncTools with correct schemas."""
        async with (
            mcp_server("http") as server_url,
            streamablehttp_client(server_url, name="test-server") as client,
        ):
            tools = await client.list_tools()
            assert len(tools) == 2

            # Check we got the expected tools
            tool_names = {tool.name for tool in tools}
            assert tool_names == {"greet", "answer_ultimate_question"}

            # Verify greet tool schema with snapshot
            greet_tool = next(t for t in tools if t.name == "greet")
            assert greet_tool.description == snapshot(
                """\
Greet a user with very special welcome.

Args:
    name: The name of the person to greet

Returns:
    A personalized welcome message\
"""
            )
            assert greet_tool.parameters.model_dump(
                by_alias=True, exclude_none=True
            ) == snapshot(
                {
                    "properties": {
                        "name": {
                            "title": "Name",
                            "type": "string",
                        }
                    },
                    "required": ["name"],
                    "additionalProperties": False,
                }
            )

            # Verify answer_ultimate_question tool schema with snapshot
            answer_tool = next(t for t in tools if t.name == "answer_ultimate_question")
            assert answer_tool.description == snapshot(
                """\
Answer the ultimate question of life, the universe, and everything.

Returns:
    A structured answer with metadata about the computation\
"""
            )
            assert answer_tool.parameters.model_dump(
                by_alias=True, exclude_none=True
            ) == snapshot(
                {"properties": {}, "required": [], "additionalProperties": False}
            )

    @pytest.mark.asyncio
    async def test_tool_execution(self) -> None:
        """Test that MCP tools can be executed via ToolCall."""
        async with (
            mcp_server("http") as server_url,
            streamablehttp_client(server_url, name="test-server") as client,
        ):
            tools = await client.list_tools()

            # Test greet tool execution
            greet_tool = next(t for t in tools if t.name == "greet")
            greet_call = llm.ToolCall(
                id="call_123", name="greet", args='{"name": "Alice"}'
            )
            greet_output = await greet_tool.execute(greet_call)

            assert greet_output.id == "call_123"
            assert greet_output.name == "greet"
            assert greet_output.value == snapshot(
                [
                    {
                        "type": "text",
                        "text": "Welcome to Zombo.com, Alice",
                        "annotations": None,
                        "meta": None,
                    }
                ]
            )

            # Test answer_ultimate_question tool execution
            answer_tool = next(t for t in tools if t.name == "answer_ultimate_question")
            answer_call = llm.ToolCall(
                id="call_456", name="answer_ultimate_question", args="{}"
            )
            answer_output = await answer_tool.execute(answer_call)

            assert answer_output.id == "call_456"
            assert answer_output.name == "answer_ultimate_question"
            assert answer_output.value == snapshot(
                [
                    {
                        "type": "text",
                        "text": """\
{
  "answer": 42,
  "question": "What is the answer to life, the universe, and everything?",
  "computed_by": {
    "name": "Deep Thought",
    "years_computed": 7500000
  }
}\
""",
                        "annotations": None,
                        "meta": None,
                    }
                ]
            )


class TestTransportModes:
    """Tests for different MCP transport modes (stdio, SSE, HTTP).

    These tests verify that each transport mode can successfully establish
    a connection to an MCP server.
    """

    @pytest.mark.asyncio
    async def test_stdio_transport(self) -> None:
        """Test that stdio transport successfully connects to MCP server."""
        async with (
            mcp_server("stdio") as server_params,
            stdio_client(server_params, name="stdio-test") as client,
        ):
            assert isinstance(client, MCPClient)
            assert client.session is not None
            assert client.name == "stdio-test"

    @pytest.mark.asyncio
    async def test_sse_transport(self) -> None:
        """Test that SSE transport successfully connects to MCP server."""
        async with (
            mcp_server("sse") as sse_url,
            sse_client(sse_url, name="sse-test") as client,
        ):
            assert isinstance(client, MCPClient)
            assert client.session is not None
            assert client.name == "sse-test"

    @pytest.mark.asyncio
    async def test_http_transport(self) -> None:
        """Test that HTTP transport successfully connects to MCP server."""
        async with (
            mcp_server("http") as http_url,
            streamablehttp_client(http_url, name="http-test") as client,
        ):
            assert isinstance(client, MCPClient)
            assert client.session is not None
            assert client.name == "http-test"
