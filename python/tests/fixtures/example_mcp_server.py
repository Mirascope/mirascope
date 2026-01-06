"""Example MCP server for testing purposes.

This server provides various tools for testing MCP client functionality
across unit, integration, and e2e tests.
"""

from __future__ import annotations

import argparse

from fastmcp import FastMCP

test_server = FastMCP("mirascope-test-server")

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
