"""MCP compatibility module."""

from .mcp_client import MCPClient, sse_client, stdio_client, streamablehttp_client

__all__ = ["MCPClient", "sse_client", "stdio_client", "streamablehttp_client"]
