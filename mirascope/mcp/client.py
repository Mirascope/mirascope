import base64
import string
from collections.abc import Awaitable, Callable
from typing import Any, ClassVar, TypeVar

from mcp import ClientSession
from mcp.types import (
    BlobResourceContents,
    CallToolResult,
    EmbeddedResource,
    ImageContent,
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
from mirascope.core.base._utils import convert_base_model_to_base_tool

_BaseToolT = TypeVar("_BaseToolT", bound=BaseTool)


class MCPClientTool(BaseTool):
    __call_tool__: ClassVar[Callable[[str, dict], Awaitable[CallToolResult]] | None] = (
        None
    )

    async def call(self) -> list[str | ImageContent | EmbeddedResource]:
        kwargs = self.model_dump()
        result = await self.__call_tool__(self._name(), kwargs)
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
        decoded_image = base64.b64decode(content.dat)

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
            mime_type = resource.mime_type
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


def json_schema_to_python_type(schema: dict[str, Any], name: str = "Model") -> Any:
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


def _create_model_from_prompt(prompt: Prompt) -> type[BaseModel]:
    if not prompt.arguments:
        return create_model(prompt.name, __base__=MCPClientTool)

    fields = {}
    for arg in prompt.arguments:
        if arg.required:
            default = Field(..., description=arg.description)
            annotation = str
        else:
            default = Field(None, description=arg.description)
            annotation = str | None

        fields[arg.name] = annotation, default

    return create_model(prompt.name, __base__=MCPClientTool, **fields)


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
            uri if isinstance(uri, AnyUrl) else uri
        )
        parsed_results = []
        for content in result.contents:
            if isinstance(result, BlobResourceContents):
                parsed_results.append(result)
            else:
                parsed_results.append(content.text)
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

    async def list_tools(self) -> list[type[MCPClientTool]]:
        list_tool_result = await self.session.list_tools()

        converted_tools = []
        for tool in list_tool_result.tools:
            model = create_model_from_tool(tool)

            class CustomMCPTool(MCPClientTool):
                __call_tool__ = self.session.call_tool
                __custom_name__ = tool.name

            converted_tools.append(
                convert_base_model_to_base_tool(model, CustomMCPTool)
            )
        return converted_tools
