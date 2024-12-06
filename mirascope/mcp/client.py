import base64
import string
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Any, TypeVar

from anyio import create_memory_object_stream, create_task_group
from anyio.streams.memory import MemoryObjectReceiveStream
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.types import (
    BlobResourceContents,
    CallToolResult,
    EmbeddedResource,
    ImageContent,
    JSONRPCMessage,
    Prompt,
    PromptMessage,
    Resource,
    TextContent,
    TextResourceContents,
    Tool,
)
from pydantic import AnyUrl, BaseModel, ConfigDict, Field, create_model

from mirascope.core import BaseMessageParam, BaseTool
from mirascope.core.base import AudioPart, DocumentPart, ImagePart

_BaseToolT = TypeVar("_BaseToolT", bound=BaseTool)


def _create_tool_call(
    name: str,
    call_tool: Callable[[str, dict | None], Awaitable[CallToolResult]],
) -> Callable[..., Awaitable[list[str | ImageContent | EmbeddedResource]]]:
    async def call(self: BaseTool) -> list[str | ImageContent | EmbeddedResource]:
        result = await call_tool(name, self.args)  # pyright: ignore [reportOptionalCall]
        if result.isError:
            raise RuntimeError(f"MCP Server returned error: {self._name()}")
        parsed_results = []
        for content in result.content:
            if isinstance(content, TextContent):
                parsed_results.append(content.text)
            else:
                parsed_results.append(content)
        return [
            content.text if isinstance(content, TextContent) else content
            for content in result.content
        ]

    return call


def _convert_prompt_message_to_base_message_params(
    prompt_message: PromptMessage,
) -> BaseMessageParam:
    """
    Convert a single PromptMessage back into a BaseMessageParam.

    Args:
        prompt_message: A PromptMessage instance.

    Returns:
        A BaseMessageParam instance representing the given prompt_message.

    Raises:
        ValueError: If the role is invalid or if the content type is unsupported.
    """

    # Validate role
    if prompt_message.role not in ["user", "assistant"]:
        raise ValueError(f"invalid role: {prompt_message.role}")

    content = prompt_message.content

    # Handle TextContent
    if isinstance(content, TextContent):
        # If it's text, we can just return a single string
        return BaseMessageParam(role=prompt_message.role, content=content.text)

    # Handle ImageContent
    elif isinstance(content, ImageContent):
        decoded_image = base64.b64decode(content.data)

        image_part = ImagePart(
            type="image",
            image=decoded_image,
            media_type=content.mimeType,
            detail=None,  # detail not provided by PromptMessage
        )
        return BaseMessageParam(role=prompt_message.role, content=[image_part])

    elif isinstance(content, EmbeddedResource):
        resource = content.resource
        if isinstance(resource, TextResourceContents):
            return BaseMessageParam(role=prompt_message.role, content=resource.text)
        else:
            mime_type = resource.mimeType
            if not mime_type:
                raise ValueError(
                    "BlobResourceContents has no mimeType, cannot determine content type."
                )

            decoded_data = base64.b64decode(resource.blob)

            if mime_type.startswith("image/"):
                # Treat as ImagePart
                image_part = ImagePart(
                    type="image",
                    image=decoded_data,
                    media_type=mime_type,
                    detail=None,
                )
                return BaseMessageParam(role=prompt_message.role, content=[image_part])
            elif mime_type == "application/pdf":
                doc_part = DocumentPart(
                    type="document", media_type=mime_type, document=decoded_data
                )
                return BaseMessageParam(role=prompt_message.role, content=[doc_part])
            elif mime_type.startswith("audio/"):
                # Treat as AudioPart
                audio_part = AudioPart(
                    type="audio", media_type=mime_type, audio=decoded_data
                )
                return BaseMessageParam(role=prompt_message.role, content=[audio_part])
            else:
                raise ValueError(f"Unsupported mime type: {mime_type}")

    else:
        raise ValueError(f"Unsupported content type: {type(content)}")


def snake_to_pascal(snake: str) -> str:
    return string.capwords(snake.replace("_", " ")).replace(" ", "")


def build_object_type(
    properties: dict[str, Any], required: list[str], name: str
) -> type[BaseModel]:
    fields = {}
    for prop_name, prop_schema in properties.items():
        class_name = snake_to_pascal(prop_name)
        type_ = json_schema_to_python_type(prop_schema, class_name)
        if prop_name in required:
            fields[prop_name] = (
                type_,
                Field(..., description=prop_schema.get("description")),
            )
        else:
            fields[prop_name] = (
                type_ | None,
                Field(None, description=prop_schema.get("description")),
            )

    return create_model(name, __config__=ConfigDict(extra="allow"), **fields)


def json_schema_to_python_type(schema: dict[str, Any], name: str = "Model") -> Any:  # noqa: ANN401
    """
    Recursively convert a JSON Schema snippet into a Python type annotation or a dynamically generated pydantic model.
    """
    json_type = schema.get("type", "any")

    if json_type == "string":
        return str
    elif json_type == "number":
        return float
    elif json_type == "integer":
        return int
    elif json_type == "boolean":
        return bool
    elif json_type == "array":
        # Recursively determine the items type for arrays
        items_schema = schema.get("items", {})
        items_type = json_schema_to_python_type(items_schema)
        return list[items_type]
    elif json_type == "object":
        # Recursively build a dynamic model for objects
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        return build_object_type(properties, required, name)
    else:
        # Default fallback
        return Any


def create_model_from_tool(tool: Tool) -> type[BaseModel]:
    """
    Create a dynamic pydantic model from the given Tool instance based on its inputSchema.
    """
    schema = tool.inputSchema
    properties = schema.get("properties", {})
    required_fields = schema.get("required", [])

    fields = {}
    for field_name, field_schema in properties.items():
        field_type = json_schema_to_python_type(field_schema)

        if field_name in required_fields:
            default = Field(..., description=field_schema.get("description"))
            annotation = field_type
        else:
            default = Field(None, description=field_schema.get("description"))
            annotation = field_type | None

        fields[field_name] = (annotation, default)

    return create_model(
        snake_to_pascal(tool.name), __config__=ConfigDict(extra="allow"), **fields
    )


class MCPClient:
    def __init__(self, session: ClientSession) -> None:
        self.session: ClientSession = session

    async def list_resources(self) -> list[Resource]:
        result = await self.session.list_resources()
        return result.resources

    async def read_resource(
        self, uri: str | AnyUrl
    ) -> list[str | BlobResourceContents]:
        result = await self.session.read_resource(
            uri if isinstance(uri, AnyUrl) else AnyUrl(uri)
        )
        parsed_results = []
        for content in result.contents:
            if isinstance(content, TextResourceContents):
                parsed_results.append(content.text)
            else:
                parsed_results.append(content)
        return parsed_results

    async def list_prompts(self) -> list[Prompt]:
        result = await self.session.list_prompts()
        return result.prompts

    async def get_prompt_template(
        self, name: str
    ) -> Callable[..., Awaitable[list[BaseMessageParam]]]:
        async def async_prompt(**kwargs: str) -> list[BaseMessageParam]:
            result = await self.session.get_prompt(name, kwargs)

            return [
                _convert_prompt_message_to_base_message_params(prompt_message)
                for prompt_message in result.messages
            ]

        return async_prompt

    async def list_tools(self) -> list[type[BaseModel]]:
        list_tool_result = await self.session.list_tools()

        converted_tools = []
        for tool in list_tool_result.tools:
            model = create_model_from_tool(tool)
            model.call = _create_tool_call(tool.name, self.session.call_tool)  # pyright: ignore [reportAttributeAccessIssue]
            converted_tools.append(model)
        return converted_tools


@asynccontextmanager
async def read_stream_exception_filer(
    original_read: MemoryObjectReceiveStream[JSONRPCMessage | Exception],
    exception_handler: Callable[[Exception], None] | None = None,
) -> AsyncGenerator[MemoryObjectReceiveStream[JSONRPCMessage], None]:
    """
    Handle exceptions in the original stream.
    default handler is to ignore read stream exception for invalid JSON lines and log them.
    Args:
        original_read: The original stream to read from.
        exception_handler: An optional handler for exception.
    """
    read_stream_writer, filtered_read = create_memory_object_stream(0)

    async def task() -> None:
        try:
            async with original_read:
                async for msg in original_read:
                    if isinstance(msg, Exception):
                        if exception_handler:
                            exception_handler(msg)
                        continue
                    await read_stream_writer.send(msg)
        finally:
            await read_stream_writer.aclose()

    async with create_task_group() as tg:
        tg.start_soon(task)
        try:
            yield filtered_read
        finally:
            await filtered_read.aclose()
            tg.cancel_scope.cancel()


@asynccontextmanager
async def create_mcp_client(
    server_parameters: StdioServerParameters,
    read_stream_exception_handler: Callable[[Exception], None] | None = None,
) -> AsyncGenerator[MCPClient, None]:
    """
    Create a MCPClient instance with the given server parameters and exception handler.

    Args:
        server_parameters:
        read_stream_exception_handler:

    Returns:

    """
    async with (
        stdio_client(server_parameters) as (read, write),
        read_stream_exception_filer(
            read, read_stream_exception_handler
        ) as filtered_read,
        ClientSession(filtered_read, write) as session,
    ):
        await session.initialize()
        yield MCPClient(session)
