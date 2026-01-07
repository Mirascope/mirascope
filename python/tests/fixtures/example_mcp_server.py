"""Example MCP server for testing purposes.

This server provides various tools for testing MCP client functionality
across unit, integration, and e2e tests.
"""

import argparse

from fastmcp import FastMCP
from pydantic import BaseModel, Field


# Define models before creating server
class ComputerInfo(BaseModel):
    """Information about Deep Thought computer."""

    name: str = Field(description="The name of the computer")
    years_computed: int = Field(description="How many years it took to compute")


class UltimateAnswer(BaseModel):
    """The answer to life, the universe, and everything."""

    answer: int = Field(description="The numerical answer")
    question: str = Field(description="The question that was asked")
    computed_by: ComputerInfo = Field(description="Information about the computer")


test_server = FastMCP("mirascope-test-server")


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
