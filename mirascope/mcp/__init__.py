"""Mirascope Model Context Protocol (MCP) implementation."""

import warnings

# The client module is the primary focus going forward
from .client import MCPClient

# Deprecated server-side implementation that will be removed in future versions
from .server import MCPServer
from .tools import MCPTool

__all__ = ["MCPClient", "MCPServer", "MCPTool"]

# Show a global deprecation warning for the server module
warnings.warn(
    "The server-side MCP implementation (MCPServer, MCPTool) is deprecated and will be removed "
    "in a future version. Mirascope will only implement the client-side of MCP (MCPClient) in the future. "
    "We recommend using the official MCP SDK (e.g. `FastMCP`) for server-side implementations.",
    DeprecationWarning,
    stacklevel=2,
)
