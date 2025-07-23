from mcp import ClientSession

from ..tools import AsyncTool


class MCPClient(ClientSession):
    """The SSE client session that connects to the MCP server.

    All of the results from the server are converted into Mirascope-friendly types.
    """

    def __init__(self, session: ClientSession) -> None:
        raise NotImplementedError()

    async def list_tools(self) -> list[AsyncTool]:  # pyright: ignore [reportIncompatibleMethodOverride]
        """List all tools available on the MCP server.

        Returns:
            A list of dynamically created `llm.Tool`s.
        """
        raise NotImplementedError()
