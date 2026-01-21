"""End-to-end tests for LLM call with MCP tools integration."""

import pytest

from mirascope import llm
from tests.llm.mcp.example_mcp_client import example_mcp_client
from tests.utils import (
    Snapshot,
    snapshot_test,
)

# Spinning up the MCP server has nontrivial overhead, and the behavior under
# test here is totally provider-independent. So we test only one model
# to minimize bloat in test time.
MCP_MODEL_IDS = ["anthropic/claude-haiku-4-5"]


@pytest.mark.parametrize("model_id", MCP_MODEL_IDS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_call_with_mcp_tools(
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test a call using tools loaded from an MCP server."""

    # Connect to MCP server and get available tools
    # Use stdio for reliability and to avoid interactions with vcr
    async with example_mcp_client("stdio") as mcp_client:
        mcp_tools = await mcp_client.list_tools()

        @llm.call(model_id, tools=mcp_tools)
        async def use_mcp_tools() -> list[llm.Message]:
            return [
                llm.messages.system(
                    "You have access to MCP tools. Use them as needed."
                ),
                llm.messages.user(
                    "Please call the greet tool with name 'Mirascope', "
                    "then call the answer_ultimate_question tool. "
                    "Finally, try using the process_answer tool to see what it does. "
                    "Report what you learn from all tools."
                ),
            ]

        with snapshot_test(snapshot, caplog) as snap:
            response = await use_mcp_tools()

            while response.tool_calls:
                tool_outputs = await response.execute_tools()
                response = await response.resume(tool_outputs)

            snap.set_response(response)
            pretty = response.pretty()

            # Verify the LLM used both tools
            assert "zombo" in pretty.lower(), (
                f"Expected greeting response to mention Zombo.com: {pretty}"
            )
            assert "42" in pretty, f"Expected answer to mention 42: {pretty}"
