"""Tests for Mirascope MCP client functionality."""

from __future__ import annotations

import anyio
import pytest
from inline_snapshot import snapshot

from mirascope import llm

from .example_mcp_client import example_mcp_client


@pytest.mark.asyncio
class TestMCPClient:
    """Integration tests for MCPClient basic functionality."""

    async def test_mcp_session(self) -> None:
        """Test that the session is correctly setup."""
        async with example_mcp_client("stdio") as client:
            assert client.session is not None

    async def test_list_tools(self) -> None:
        """Test that list_tools returns Mirascope AsyncTools with correct schemas."""
        async with example_mcp_client("stdio") as client:
            tools = await client.list_tools()
            assert len(tools) == 3

            # Check we got the expected tools
            tool_names = {tool.name for tool in tools}
            assert tool_names == {"greet", "answer_ultimate_question", "process_answer"}

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
                    "properties": {"name": {"type": "string"}},
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

            # Verify process_answer tool schema with $defs
            process_tool = next(t for t in tools if t.name == "process_answer")
            assert process_tool.description == snapshot(
                """\
Process and format an ultimate answer.

This tool demonstrates complex schema with $defs by accepting
a nested Pydantic model as input.

Args:
    answer_data: The answer data to process

Returns:
    A formatted string describing the answer\
"""
            )
            schema = process_tool.parameters.model_dump(
                by_alias=True, exclude_none=True
            )
            # Verify $defs is present and contains the nested model definitions
            assert "$defs" in schema
            assert "ComputerInfo" in schema["$defs"]
            assert "UltimateAnswer" in schema["$defs"]
            # Full schema snapshot
            assert schema == snapshot(
                {
                    "properties": {
                        "answer_data": {"$ref": "#/$defs/UltimateAnswer"},
                    },
                    "required": ["answer_data"],
                    "additionalProperties": False,
                    "$defs": {
                        "ComputerInfo": {
                            "properties": {
                                "name": {
                                    "description": "The name of the computer",
                                    "type": "string",
                                },
                                "years_computed": {
                                    "description": "How many years it took to compute",
                                    "type": "integer",
                                },
                            },
                            "required": ["name", "years_computed"],
                            "description": "Information about Deep Thought computer.",
                            "type": "object",
                        },
                        "UltimateAnswer": {
                            "description": "The answer to life, the universe, and everything.",
                            "properties": {
                                "answer": {
                                    "description": "The numerical answer",
                                    "type": "integer",
                                },
                                "question": {
                                    "description": "The question that was asked",
                                    "type": "string",
                                },
                                "computed_by": {
                                    "$ref": "#/$defs/ComputerInfo",
                                    "description": "Information about the computer",
                                },
                            },
                            "required": ["answer", "question", "computed_by"],
                            "type": "object",
                        },
                    },
                }
            )

    async def test_tool_execution(self) -> None:
        """Test that MCP tools can be executed via ToolCall."""
        async with example_mcp_client("stdio") as client:
            tools = await client.list_tools()

            # Test greet tool execution
            greet_tool = next(t for t in tools if t.name == "greet")
            greet_call = llm.ToolCall(
                id="call_123", name="greet", args='{"name": "Alice"}'
            )
            greet_output = await greet_tool.execute(greet_call)

            assert greet_output.id == "call_123"
            assert greet_output.name == "greet"
            assert greet_output.result == snapshot(
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
            assert answer_output.result == snapshot(
                [
                    {
                        "type": "text",
                        "text": '{"answer":42,"question":"What is the answer to life, the universe, and everything?","computed_by":{"name":"Deep Thought","years_computed":7500000}}',
                        "annotations": None,
                        "meta": None,
                    }
                ]
            )

            # Test process_answer tool execution with complex nested input
            process_tool = next(t for t in tools if t.name == "process_answer")
            process_call = llm.ToolCall(
                id="call_789",
                name="process_answer",
                args="""{
                    "answer_data": {
                        "answer": 81,
                        "question": "What is 9 * 9?",
                        "computed_by": {
                            "name": "Simple Thought",
                            "years_computed": 3
                        }
                    }
                }""",
            )
            process_output = await process_tool.execute(process_call)

            assert process_output.id == "call_789"
            assert process_output.name == "process_answer"
            assert process_output.result == snapshot(
                [
                    {
                        "type": "text",
                        "text": "The answer 81 to 'What is 9 * 9?' was computed by Simple Thought over 3 years",
                        "annotations": None,
                        "meta": None,
                    }
                ]
            )

    async def test_tool_execution_after_client_closed(self) -> None:
        """Test the failure case when calling mcp tools after the client connection is closed."""
        async with example_mcp_client("stdio") as client:
            tools = await client.list_tools()

        greet_tool = next(t for t in tools if t.name == "greet")
        greet_call = llm.ToolCall(id="call_123", name="greet", args='{"name": "Alice"}')
        # Client now closed! Error is captured in ToolOutput
        output = await greet_tool.execute(greet_call)
        assert output.error is not None
        assert isinstance(output.error, llm.ToolExecutionError)
        assert isinstance(output.error.tool_exception, anyio.ClosedResourceError)


@pytest.mark.asyncio
@pytest.mark.skip("Flaky — run manually if changing transport code")
class TestTransportModes:
    """Tests for different MCP transport modes (SSE, HTTP).

    These tests verify that each transport mode can successfully establish
    a connection to an MCP server.

    Note: The stdio approach is the most reliable and is used in other testing, but we
    include it here for completeness.

    The sse and http connections run into teardown/flakiness issues.
    """

    async def test_stdio_transport(self) -> None:
        """Test that stdio transport successfully connects to MCP server."""
        async with example_mcp_client("stdio") as client:
            assert isinstance(client, llm.mcp.MCPClient)
            assert client.session is not None

    async def test_sse_transport(self) -> None:
        """Test that SSE transport successfully connects to MCP server."""
        async with example_mcp_client("sse") as client:
            assert isinstance(client, llm.mcp.MCPClient)
            assert client.session is not None

    async def test_http_transport(self) -> None:
        """Test that HTTP transport successfully connects to MCP server."""
        async with example_mcp_client("http") as client:
            assert isinstance(client, llm.mcp.MCPClient)
            assert client.session is not None
