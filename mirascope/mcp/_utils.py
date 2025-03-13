"""MCP client utility functions."""

import base64
import string
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Any

from anyio import create_memory_object_stream, create_task_group
from anyio.streams.memory import MemoryObjectReceiveStream
from mcp.types import (
    EmbeddedResource,
    ImageContent,
    JSONRPCMessage,
    PromptMessage,
    TextContent,
    TextResourceContents,
)
from mcp.types import Tool as MCPTool
from pydantic import BaseModel, ConfigDict, Field, create_model

from ..core import BaseMessageParam, BaseTool
from ..core.base import AudioPart, DocumentPart, ImagePart


def create_tool_call(
    name: str,
    call_tool: Callable[[str, dict | None], Awaitable[Any]],
) -> Callable[..., Awaitable[list[str | ImageContent | EmbeddedResource]]]:
    """Create a tool call function for a Mirascope Tool.

    Args:
        name: The name of the tool
        call_tool: The function to call the tool

    Returns:
        A function that can be used as the call method for a Tool
    """

    async def call(self: BaseTool) -> list[str | ImageContent | EmbeddedResource]:
        result = await call_tool(name, self.args)  # pyright: ignore [reportOptionalCall]
        if result.isError:
            raise RuntimeError(f"MCP Server returned error: {self._name()}")
        return [
            content.text if isinstance(content, TextContent) else content
            for content in result.content
        ]

    return call


def convert_prompt_message_to_base_message_params(
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
            # For text content embedded resources, just return the text
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
    """Convert a snake_case string to PascalCase.

    Args:
        snake: A snake_case string

    Returns:
        The string converted to PascalCase
    """
    return string.capwords(snake.replace("_", " ")).replace(" ", "")


def build_object_type(
    properties: dict[str, Any], required: list[str], name: str
) -> type[BaseModel]:
    """Build a Pydantic model from JSON Schema properties.

    Args:
        properties: JSON Schema properties dictionary
        required: List of required property names
        name: Name for the generated model

    Returns:
        A dynamically created Pydantic model class
    """
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

    Args:
        schema: JSON Schema to convert
        name: Name for any generated models

    Returns:
        Corresponding Python type or Pydantic model
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


def create_tool_from_mcp_tool(tool: MCPTool) -> type[BaseTool]:
    """
    Create a `BaseTool` type definition from the given MCP Tool instance.

    Args:
        tool: MCP tool instance.

    Returns:
        A dynamically created `Tool` schema.
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

    return create_model(snake_to_pascal(tool.name), __base__=BaseTool, **fields)


@asynccontextmanager
async def read_stream_exception_filer(
    original_read: MemoryObjectReceiveStream[JSONRPCMessage | Exception],
    exception_handler: Callable[[Exception], None] | None = None,
) -> AsyncGenerator[MemoryObjectReceiveStream[JSONRPCMessage], None]:
    """
    Handle exceptions in the original stream.
    Default handler is to ignore read stream exception for invalid JSON lines and log them.

    Args:
        original_read: The original stream to read from.
        exception_handler: An optional handler for exception.

    Yields:
        A filtered stream with exceptions removed
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
