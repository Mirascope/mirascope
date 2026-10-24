"""Tests for Mirascope MCP client functionality."""

from __future__ import annotations

import anyio
import pytest
from inline_snapshot import snapshot
from mcp.server.lowlevel import Server
from mcp.shared.exceptions import McpError
from mcp.shared.memory import create_connected_server_and_client_session
from mcp.types import (
    INTERNAL_ERROR,
    CallToolResult,
    ErrorData,
    ListToolsRequest,
    ListToolsResult,
    TextContent,
    Tool as MCPTool,
)

from mirascope import llm

from .example_mcp_client import example_mcp_client


def _tool_page(names: list[str], next_cursor: str | None = None) -> ListToolsResult:
    return ListToolsResult(
        tools=[MCPTool(name=name, inputSchema={"type": "object"}) for name in names],
        nextCursor=next_cursor,
    )


def _paginated_server(
    pages: list[ListToolsResult | ErrorData], cursors: list[str | None]
) -> Server[dict[str, object]]:
    server = Server[dict[str, object]]("paginated-tools")

    async def list_tools(request: ListToolsRequest) -> ListToolsResult:
        cursor = request.params.cursor if request.params is not None else None
        page = pages[len(cursors)]
        cursors.append(cursor)
        if isinstance(page, ErrorData):
            raise McpError(page)
        return page

    server.list_tools()(list_tools)
    return server


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
class TestMCPToolPagination:
    @pytest.mark.parametrize(
        ("pages", "expected_names", "expected_cursors"),
        [
            (
                [_tool_page(["first"], "next"), _tool_page(["second"])],
                ["first", "second"],
                [None, "next"],
            ),
            (
                [
                    _tool_page(["first"], "opaque/+==? page=2"),
                    _tool_page(["second"], "third-page"),
                    _tool_page(["third"]),
                ],
                ["first", "second", "third"],
                [None, "opaque/+==? page=2", "third-page"],
            ),
            (
                [
                    _tool_page(["first"], "empty-page"),
                    _tool_page([], "last-page"),
                    _tool_page(["last"]),
                ],
                ["first", "last"],
                [None, "empty-page", "last-page"],
            ),
            (
                [_tool_page([], "next"), _tool_page(["second"])],
                ["second"],
                [None, "next"],
            ),
            (
                [_tool_page(["first"], ""), _tool_page(["second"])],
                ["first", "second"],
                [None, ""],
            ),
            ([_tool_page([])], [], [None]),
        ],
        ids=[
            "two-pages",
            "opaque-three-pages",
            "empty-middle",
            "empty-first",
            "empty-cursor",
            "empty-result",
        ],
    )
    async def test_list_all_pages(
        self,
        pages: list[ListToolsResult | ErrorData],
        expected_names: list[str],
        expected_cursors: list[str | None],
    ) -> None:
        cursors: list[str | None] = []
        server = _paginated_server(pages, cursors)
        async with create_connected_server_and_client_session(server) as session:
            tools = await llm.mcp.MCPClient(session).list_tools()
            assert [tool.name for tool in tools] == expected_names
            assert cursors == expected_cursors

    @pytest.mark.parametrize("cursor", ["repeated", ""])
    async def test_rejects_repeated_cursor(self, cursor: str) -> None:
        cursors: list[str | None] = []
        server = _paginated_server(
            [_tool_page(["first"], cursor), _tool_page(["second"], cursor)],
            cursors,
        )
        async with create_connected_server_and_client_session(server) as session:
            with pytest.raises(ValueError, match="repeated pagination cursor"):
                await llm.mcp.MCPClient(session).list_tools()
            assert cursors == [None, cursor]

    async def test_rejects_cursor_cycle(self) -> None:
        cursors: list[str | None] = []
        server = _paginated_server(
            [
                _tool_page(["first"], "second-page"),
                _tool_page(["second"], "third-page"),
                _tool_page(["third"], "second-page"),
            ],
            cursors,
        )
        async with create_connected_server_and_client_session(server) as session:
            with pytest.raises(ValueError, match="repeated pagination cursor"):
                await llm.mcp.MCPClient(session).list_tools()
            assert cursors == [None, "second-page", "third-page"]

    async def test_later_page_error_propagates(self) -> None:
        cursors: list[str | None] = []
        server = _paginated_server(
            [
                _tool_page(["first"], "next"),
                ErrorData(code=INTERNAL_ERROR, message="later page failed"),
            ],
            cursors,
        )
        async with create_connected_server_and_client_session(server) as session:
            with pytest.raises(McpError, match="later page failed") as exception_info:
                await llm.mcp.MCPClient(session).list_tools()
            assert exception_info.value.error.code == INTERNAL_ERROR
            assert cursors == [None, "next"]

    async def test_tool_from_second_page_executes(self) -> None:
        cursors: list[str | None] = []
        calls: list[str] = []
        server = _paginated_server(
            [_tool_page(["first"], "next"), _tool_page(["second"])], cursors
        )

        async def call_tool(name: str, arguments: dict[str, object]) -> CallToolResult:
            calls.append(name)
            return CallToolResult(
                content=[TextContent(type="text", text=f"{name} ran")]
            )

        server.call_tool()(call_tool)
        async with create_connected_server_and_client_session(server) as session:
            tools = await llm.mcp.MCPClient(session).list_tools()
            second = next(tool for tool in tools if tool.name == "second")
            result = await second.execute(
                llm.ToolCall(id="second-call", name="second", args="{}")
            )
            assert result.error is None
            assert result.result == [
                TextContent(type="text", text="second ran").model_dump()
            ]
            assert calls == ["second"]
            assert cursors == [None, "next"]

    async def test_tool_error_result_is_reported_as_error(self) -> None:
        server = _paginated_server([_tool_page(["failing"])], [])

        async def call_tool(name: str, arguments: dict[str, object]) -> CallToolResult:
            return CallToolResult(
                content=[TextContent(type="text", text="disk is full")], isError=True
            )

        server.call_tool(validate_input=False)(call_tool)
        async with create_connected_server_and_client_session(server) as session:
            tools = await llm.mcp.MCPClient(session).list_tools()
            result = await tools[0].execute(
                llm.ToolCall(id="failing-call", name="failing", args="{}")
            )
            assert isinstance(result.error, llm.ToolExecutionError)
            assert "disk is full" in str(result.result)


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
