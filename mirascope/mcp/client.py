"""The `MCPServer` Class and context managers."""

import contextlib
from collections.abc import AsyncIterator, Awaitable, Callable
from datetime import timedelta
from typing import Any

from mcp import ClientSession
from mcp.client.session import ListRootsFnT, SamplingFnT
from mcp.client.sse import sse_client as mcp_sse_client
from mcp.client.stdio import StdioServerParameters
from mcp.client.stdio import stdio_client as mcp_stdio_client
from mcp.types import (
    BlobResourceContents,
    Resource,
)
from pydantic import AnyUrl

from mirascope.core import BaseMessageParam, BaseTool, TextPart
from mirascope.mcp import _utils


class MCPClient(ClientSession):
    """The SSE client session that connects to the MCP server.

    All of the results from the server are converted into Mirascope-friendly types.
    """

    _session: ClientSession

    def __init__(self, session: ClientSession) -> None:
        """Initializes an instance of `MCPClient`.

        Args:
            session: The original MCP `ClientSession`.
        """
        self._session = session

    async def list_resources(self) -> list[Resource]:  # pyright: ignore [reportIncompatibleMethodOverride]
        """List all resources available on the MCP server.

        Returns:
            A list of Resource objects
        """
        result = await self._session.list_resources()
        return result.resources

    async def read_resource(  # pyright: ignore [reportIncompatibleMethodOverride]
        self, uri: str | AnyUrl
    ) -> list[TextPart | BlobResourceContents]:
        """Read a resource from the MCP server.

        Args:
            uri: URI of the resource to read

        Returns:
            Contents of the resource, either as string or BlobResourceContents
        """
        result = await self._session.read_resource(
            uri if isinstance(uri, AnyUrl) else AnyUrl(uri)
        )
        parsed_results: list[TextPart | BlobResourceContents] = []
        for content in result.contents:
            if isinstance(content, BlobResourceContents):
                parsed_results.append(content)
            else:
                parsed_results.append(TextPart(type="text", text=content.text))
        return parsed_results

    async def list_prompts(self) -> list[Any]:  # pyright: ignore [reportIncompatibleMethodOverride]
        """List all prompts available on the MCP server.

        Returns:
            A list of Prompt objects
        """
        result = await self._session.list_prompts()
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

        # TODO: wrap this with `llm.prompt` once it's implemented so that they prompts
        # can be run super easily inside of an `llm.context` block.
        async def async_prompt(**kwargs: str) -> list[BaseMessageParam]:
            result = await self._session.get_prompt(name, kwargs)  # type: ignore

            return [
                _utils.convert_prompt_message_to_base_message_params(prompt_message)
                for prompt_message in result.messages
            ]

        return async_prompt

    async def list_tools(self) -> list[type[BaseTool]]:  # pyright: ignore [reportIncompatibleMethodOverride]
        """List all tools available on the MCP server.

        Returns:
            A list of dynamically created `BaseTool` types.
        """
        list_tool_result = await self._session.list_tools()

        converted_tools = []
        for tool in list_tool_result.tools:
            model = _utils.create_tool_from_mcp_tool(tool)
            tool_call_method = _utils.create_tool_call(
                tool.name, self._session.call_tool
            )
            model.call = tool_call_method  # pyright: ignore [reportAttributeAccessIssue]
            converted_tools.append(model)
        return converted_tools


@contextlib.asynccontextmanager
async def sse_client(
    url: str,
    list_roots_callback: ListRootsFnT | None = None,
    read_timeout_seconds: timedelta | None = None,
    sampling_callback: SamplingFnT | None = None,
    session: ClientSession | None = None,
) -> AsyncIterator[MCPClient]:
    async with (
        mcp_sse_client(url) as (read, write),
        ClientSession(
            read,
            write,
            read_timeout_seconds=read_timeout_seconds,
            sampling_callback=sampling_callback,
            list_roots_callback=list_roots_callback,
        ) as session,
    ):
        await session.initialize()
        yield MCPClient(session)


@contextlib.asynccontextmanager
async def stdio_client(
    server_parameters: StdioServerParameters,
    read_stream_exception_handler: Callable[[Exception], None] | None = None,
) -> AsyncIterator[MCPClient]:
    """
    Create a MCPClient instance with the given server parameters and exception handler.

    Args:
        server_parameters:
        read_stream_exception_handler:

    Returns:

    """
    async with (
        mcp_stdio_client(server_parameters) as (read, write),
        _utils.read_stream_exception_filer(
            read, read_stream_exception_handler
        ) as filtered_read,
        ClientSession(filtered_read, write) as session,  # pyright: ignore [reportArgumentType]
    ):
        await session.initialize()
        yield MCPClient(session)
