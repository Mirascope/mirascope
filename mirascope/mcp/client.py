"""MCP client implementation."""

from collections.abc import Awaitable, Callable
from types import TracebackType
from typing import Any

from mcp import ClientSession
from mcp.client.session import ListRootsFnT, SamplingFnT
from mcp.client.sse import sse_client
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.types import BlobResourceContents, Resource
from pydantic import AnyUrl

from mirascope.core import BaseMessageParam, BaseTool, TextPart
from mirascope.mcp import _utils


class MCPClient:
    """Client for interacting with MCP (Model Context Protocol) servers.

    This class provides methods to interact with MCP servers, listing and using
    resources, prompts, and tools defined by the server.

    Example:
    ```python
    import asyncio
    from mirascope.mcp import MCPClient
    from mcp.client.stdio import StdioServerParameters

    async def main():
        server_params = StdioServerParameters(
            command="python", args=["-m", "your_mcp_server"], env=None
        )

        async with MCPClient(server_params) as client:
            # List available tools
            tools = await client.list_tools()

            # Use a tool
            tool_instance = tools[0](param1="value")
            result = await tool_instance.call()
            print(result)

    asyncio.run(main())
    ```
    """

    def __init__(
        self,
        server_parameters: str | StdioServerParameters | None = None,
        list_roots_callback: ListRootsFnT | None = None,
        sampling_callback: SamplingFnT | None = None,
        session: ClientSession | None = None,
        read_stream_exception_handler: Callable[[Exception], None] | None = None,
    ) -> None:
        """Initialize an MCPClient instance.

        Args:
            server_parameters: Parameters for connecting to an MCP server. Required if
                session is not provided.
            session: A pre-initialized ClientSession. If provided, server_parameters is ignored.
            read_stream_exception_handler: Optional handler for stream exceptions.
        """
        if session is None and server_parameters is None:
            raise ValueError("Either session or server_parameters must be provided")

        self.session: ClientSession | None = session
        self._sampling_callback: SamplingFnT | None = sampling_callback
        self._list_roots_callback: ListRootsFnT | None = list_roots_callback
        self._server_parameters = server_parameters
        self._read_stream_exception_handler = read_stream_exception_handler
        self._read_stream = None
        self._write_stream = None

    async def __aenter__(self) -> "MCPClient":
        """Enter the async context, establishing connection to the MCP server."""
        if self.session is None and self._server_parameters is not None:
            if isinstance(self._server_parameters, str):
                async with (
                    sse_client(url=self._server_parameters) as (read, write),
                    ClientSession(
                        read,
                        write,
                        sampling_callback=self._sampling_callback,
                        list_roots_callback=self._list_roots_callback,
                    ) as session,
                ):
                    self.session = session
                    await self.session.initialize()
            else:
                self._read_stream, self._write_stream = await stdio_client(
                    self._server_parameters
                ).__aenter__()
                filtered_read = await _utils.read_stream_exception_filer(
                    self._read_stream, self._read_stream_exception_handler
                ).__aenter__()
                self.session = await ClientSession(
                    filtered_read, self._write_stream
                ).__aenter__()
                await self.session.initialize()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException],
        exc_val: BaseException | None = None,
        exc_tb: TracebackType | None = None,
    ) -> None:
        """Exit the async context, closing connection to the MCP server."""
        if self.session is not None:
            await self.session.__aexit__(exc_type, exc_val, exc_tb)
            self.session = None

        if self._read_stream is not None:
            await self._read_stream.__aexit__(exc_type, exc_val, exc_tb)
            self._read_stream = None

        if self._write_stream is not None:
            await self._write_stream.__aexit__(exc_type, exc_val, exc_tb)
            self._write_stream = None

    async def list_resources(self) -> list[Resource]:
        """List all resources available on the MCP server.

        Returns:
            A list of Resource objects
        """
        if self.session is None:
            raise RuntimeError(
                "Client not initialized. Use within an async context manager."
            )

        result = await self.session.list_resources()
        return result.resources

    async def read_resource(
        self, uri: str | AnyUrl
    ) -> list[TextPart | BlobResourceContents]:
        """Read a resource from the MCP server.

        Args:
            uri: URI of the resource to read

        Returns:
            Contents of the resource, either as string or BlobResourceContents
        """
        if self.session is None:
            raise RuntimeError(
                "Client not initialized. Use within an async context manager."
            )

        result = await self.session.read_resource(
            uri if isinstance(uri, AnyUrl) else AnyUrl(uri)
        )
        parsed_results: list[TextPart | BlobResourceContents] = []
        for content in result.contents:
            if isinstance(content, BlobResourceContents):
                parsed_results.append(content)
            else:
                parsed_results.append(TextPart(type="text", text=content.text))
        return parsed_results

    async def list_prompts(self) -> list[Any]:
        """List all prompts available on the MCP server.

        Returns:
            A list of Prompt objects
        """
        if self.session is None:
            raise RuntimeError(
                "Client not initialized. Use within an async context manager."
            )

        result = await self.session.list_prompts()
        return result.prompts

    async def get_prompt_template(
        self, name: str
    ) -> Callable[..., Awaitable[list[BaseMessageParam]]]:
        """Get a prompt template from the MCP server.

        Args:
            name: Name of the prompt template

        Returns:
            A callable that accepts keyword arguments and returns a list of BaseMessageParam
        """
        if self.session is None:
            raise RuntimeError(
                "Client not initialized. Use within an async context manager."
            )

        # TODO: wrap this with `llm.prompt` once it's implemented so that they prompts
        # can be run super easily inside of an `llm.context` block.
        async def async_prompt(**kwargs: str) -> list[BaseMessageParam]:
            result = await self.session.get_prompt(name, kwargs)  # type: ignore

            return [
                _utils.convert_prompt_message_to_base_message_params(prompt_message)
                for prompt_message in result.messages
            ]

        return async_prompt

    async def list_tools(self) -> list[type[BaseTool]]:
        """List all tools available on the MCP server.

        Returns:
            A list of dynamically created `BaseTool` types.
        """
        if self.session is None:
            raise RuntimeError(
                "Client not initialized. Use within an async context manager."
            )

        list_tool_result = await self.session.list_tools()

        converted_tools = []
        for tool in list_tool_result.tools:
            model = _utils.create_model_from_tool(tool)
            model.call = _utils.create_tool_call(tool.name, self.session.call_tool)  # pyright: ignore [reportAttributeAccessIssue]
            converted_tools.append(model)
        return converted_tools
