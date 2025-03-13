"""Mirascope Model Context Protocol (MCP) implementation."""

from .client import MCPClient, sse_client, stdio_client
from .server import MCPServer  # DEPRECATED
from .tools import MCPTool  # DEPRECATED

__all__ = ["MCPClient", "MCPServer", "MCPTool", "sse_client", "stdio_client"]
