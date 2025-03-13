"""The `MCPServer` Class and context managers."""

import inspect
import warnings
from collections.abc import Awaitable, Callable, Iterable
from typing import Literal, ParamSpec, cast, overload

import mcp.server.stdio
from docstring_parser import parse
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    GetPromptResult,
    ImageContent,
    Prompt,
    PromptArgument,
    PromptMessage,
    Resource,
    TextContent,
    Tool,
)
from pydantic import AnyUrl, BaseModel

from mirascope.core import BaseDynamicConfig, BaseMessageParam, BaseTool
from mirascope.core.base import ImagePart, TextPart
from mirascope.core.base._utils import (
    MessagesDecorator,
    convert_base_model_to_base_tool,
    convert_function_to_base_tool,
    fn_is_async,
)
from mirascope.core.base._utils._messages_decorator import (
    MessagesAsyncFunction,
    MessagesSyncFunction,
)
from mirascope.core.base.prompt import PromptDecorator, prompt_template
from mirascope.mcp.tools import MCPTool, ToolUseBlock

_P = ParamSpec("_P")


def _convert_base_message_param_to_prompt_messages(
    base_message_param: BaseMessageParam,
) -> list[PromptMessage]:
    """
    Convert BaseMessageParam to types.PromptMessage.

    Args:
        base_message_param: BaseMessageParam instance.

    Returns:
        A list of types.PromptMessage instances.
    """

    # Validate role
    role = base_message_param.role
    if role not in ["user", "assistant"]:
        raise ValueError(f"invalid role: {role}")

    if isinstance(base_message_param.content, str):
        contents = [TextContent(type="text", text=base_message_param.content)]
    elif isinstance(base_message_param.content, Iterable):
        contents = []
        for part in base_message_param.content:
            if isinstance(part, TextPart):
                contents.append(TextContent(type="text", text=part.text))
            elif isinstance(part, ImagePart):
                contents.append(
                    ImageContent(
                        type="image",
                        data=part.image.decode("utf-8"),
                        mimeType=part.media_type,
                    )
                )
            else:
                raise ValueError(f"Unsupported content type: {type(part)}")
    else:
        raise ValueError(
            f"Unsupported content type: {type(base_message_param.content)}"
        )

    return [
        PromptMessage(role=cast(Literal["user", "assistant"], role), content=content)
        for content in contents
    ]


def _generate_prompt_from_function(fn: Callable) -> Prompt:
    """
    Generate a Prompt object from a function, extracting metadata like argument descriptions
    from the function's docstring and type hints.

    Args:
        fn (Callable): The function to process.

    Returns:
        Prompt: A structured Prompt object with metadata.
    """
    # Parse the docstring for structured information
    docstring = parse(fn.__doc__ or "")

    # Extract general description from the docstring
    description = docstring.short_description or ""

    # Prepare to extract argument details
    signature = inspect.signature(fn)
    parameter_docs = {param.arg_name: param.description for param in docstring.params}

    arguments = []
    for parameter in signature.parameters.values():
        arg_desc = parameter_docs.get(parameter.name, "")
        required = parameter.default is inspect.Parameter.empty
        arguments.append(
            PromptArgument(name=parameter.name, description=arg_desc, required=required)
        )

    return Prompt(name=fn.__name__, description=description, arguments=arguments)


class MCPServer:
    """MCP server implementation.

    DEPRECATED: The MCPServer implementation is deprecated and will be removed in a future version.
    Mirascope will only implement the client-side of MCP in the future, allowing it to connect to any
    MCP server implementation, even if not built with Mirascope.
    """

    def __init__(
        self,
        name: str,
        version: str = "1.0.0",
        tools: list[Callable | type[BaseTool]] | None = None,
        resources: list[tuple[Resource, Callable]] | None = None,
        prompts: list[
            Callable[
                ...,
                list[BaseMessageParam]
                | Callable[..., Awaitable[list[BaseMessageParam]]],
            ]
        ]
        | None = None,
    ) -> None:
        warnings.warn(
            "MCPServer is deprecated and will be removed in a future version. "
            "Mirascope will only implement the client-side of MCP in the future. "
            "We recommend using the official MCP SDK (e.g. `FastMCP`) for server-side implementations.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.name: str = name
        self.version: str = version
        self.server: Server = Server(name)
        self._tools: dict[str, tuple[Tool, type[MCPTool]]] = {}
        self._resources: dict[str, tuple[Resource, Callable]] = {}
        self._prompts: dict[
            str,
            tuple[
                Prompt,
                Callable[..., Awaitable[list[BaseMessageParam]]]
                | Callable[..., list[BaseMessageParam]],
            ],
        ] = {}
        if tools:
            for tool in tools:
                self.tool()(tool)
        if resources:
            for resource, resource_func in resources:
                self.resource(
                    uri=str(resource.uri),
                    name=resource.name,
                    description=resource.description,
                    mime_type=resource.mimeType,
                )(resource_func)
        if prompts:
            for prompt in prompts:
                self._register_prompt(prompt)

    def tool(
        self,
    ) -> Callable[[Callable | type[BaseTool]], type[BaseTool]]:
        """Decorator to register tools."""

        def decorator(
            tool: Callable | type[BaseTool],
        ) -> type[BaseTool]:
            if inspect.isclass(tool):
                if issubclass(tool, MCPTool):
                    converted_tool = tool
                else:
                    converted_tool = convert_base_model_to_base_tool(
                        cast(type[BaseModel], tool), MCPTool
                    )
            else:
                converted_tool = convert_function_to_base_tool(tool, MCPTool)
            tool_schema = converted_tool.tool_schema()
            name = tool_schema["name"]
            if name in self._tools:
                # Raise KeyError if tool name already exists
                raise KeyError(f"Tool {name} already exists.")

            self._tools[name] = (
                Tool(
                    name=name,
                    description=tool_schema.get("description"),
                    inputSchema=tool_schema["input_schema"],
                ),
                converted_tool,
            )
            return converted_tool

        return decorator

    def resource(
        self,
        uri: str,
        name: str | None = None,
        description: str | None = None,
        mime_type: str | None = None,
    ) -> Callable[[Callable], Callable]:
        """Decorator to register resources."""

        def decorator(func: Callable) -> Callable:
            # Normalize URI so it always ends with a slash if needed
            uri_with_slash = uri + "/" if not uri.endswith("/") else uri

            if uri_with_slash in self._resources:
                # Raise KeyError if resource URI already exists
                raise KeyError(f"Resource {uri_with_slash} already exists.")

            resource = Resource(
                uri=cast(AnyUrl, uri_with_slash),
                name=name or func.__name__,
                mimeType=mime_type,
                description=description
                or parse(func.__doc__ or "").short_description
                or "",
            )
            self._resources[str(resource.uri)] = resource, func
            return func

        return decorator

    def _register_prompt(self, decorated_func: Callable) -> None:
        prompt = _generate_prompt_from_function(decorated_func)
        name = prompt.name
        if name in self._prompts:
            # Raise KeyError if prompt name already exists
            raise KeyError(f"Prompt {name} already exists.")

        self._prompts[prompt.name] = prompt, decorated_func

    @overload
    def prompt(self, template: str) -> PromptDecorator: ...

    @overload
    def prompt(self, template: None = None) -> MessagesDecorator: ...

    def prompt(
        self,
        template: str | None = None,
    ) -> PromptDecorator | MessagesDecorator:
        """Decorator to register prompts."""

        def decorator(
            func: MessagesSyncFunction | MessagesAsyncFunction,
        ) -> (
            Callable[..., Awaitable[list[BaseMessageParam] | BaseDynamicConfig]]
            | Callable[..., list[BaseMessageParam] | BaseDynamicConfig]
        ):
            decorated_prompt = prompt_template(template)(func)
            self._register_prompt(decorated_prompt)
            return decorated_prompt

        return decorator  # pyright: ignore [reportReturnType]

    async def run(self) -> None:
        """Run the MCP server."""

        @self.server.read_resource()
        async def handle_read_resource(uri: AnyUrl) -> str:
            resource_and_func = self._resources.get(str(uri))
            if resource_and_func is None:
                raise ValueError(f"Unknown resource: {uri}")

            resource, func = resource_and_func
            if fn_is_async(func):
                ret = await func()
            else:
                ret = func()
            return ret

        @self.server.list_resources()
        async def handle_list_resource() -> list[Resource]:
            return [resource for resource, _ in self._resources.values()]

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [tool for tool, _ in self._tools.values()]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            if name not in self._tools:
                raise KeyError(f"Tool {name} not found.")
            _, tool_type = self._tools[name]

            tool = tool_type.from_tool_call(
                tool_call=ToolUseBlock(id=name, name=name, input=arguments)
            )
            if fn_is_async(tool.call):
                result = await tool.call()
            else:
                result = tool.call()
            return [TextContent(type="text", text=result)]

        @self.server.list_prompts()
        async def handle_list_prompts() -> list[Prompt]:
            return [prompt for prompt, _ in self._prompts.values()]

        @self.server.get_prompt()
        async def handle_get_prompt(
            name: str, arguments: dict[str, str] | None
        ) -> GetPromptResult:
            if name not in self._prompts:
                raise ValueError(f"Unknown prompt: {name}")
            if arguments is None:
                arguments = {}
            prompt, decorated_func = self._prompts[name]
            if fn_is_async(decorated_func):
                messages: list[BaseMessageParam] = await decorated_func(**arguments)
            else:
                messages = decorated_func(**arguments)

            return GetPromptResult(
                description=f"{prompt.name} template for {arguments}",
                messages=[
                    prompt_message
                    for message in messages
                    for prompt_message in _convert_base_message_param_to_prompt_messages(
                        message
                    )
                ],
            )

        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=self.name,
                    server_version=self.version,
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
