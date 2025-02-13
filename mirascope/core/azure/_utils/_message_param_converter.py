import json
from typing import cast

from azure.ai.inference.models import (
    AssistantMessage,
    ChatRequestMessage,
    ContentItem,
    ImageContentItem,
    TextContentItem,
    ToolMessage,
    UserMessage,
)

from mirascope.core.azure._utils import convert_message_params
from mirascope.core.base import (
    BaseMessageParam,
    ImageURLPart,
    TextPart,
    ToolCallPart,
    ToolResultPart,
)
from mirascope.core.base._utils._base_message_param_converter import (
    BaseMessageParamConverter,
)


def _parse_content(content: list[ContentItem]) -> list[TextPart | ImageURLPart]:
    converted_parts = []
    for part in content:
        if isinstance(part, TextContentItem):
            converted_parts.append(TextPart(type="text", text=part.text))
        elif isinstance(part, ImageContentItem):
            converted_parts.append(
                ImageURLPart(
                    type="image_url",
                    url=part.image_url.url,
                    detail=part.image_url.detail,
                )
            )

    return converted_parts


class AzureMessageParamConverter(BaseMessageParamConverter):
    """Converts between Azure `ChatRequestMessage` / `AssistantMessage` and Mirascope `BaseMessageParam`."""

    @staticmethod
    def to_provider(message_params: list[BaseMessageParam]) -> list[ChatRequestMessage]:
        """Convert from Mirascope `BaseMessageParam` to Azure's `ChatRequestMessage`."""
        return convert_message_params(
            cast(list[BaseMessageParam | ChatRequestMessage], message_params)
        )

    @staticmethod
    def from_provider(
        message_params: list[ChatRequestMessage],
    ) -> list[BaseMessageParam]:
        """
        Convert from Azure's `AssistantMessage` back to Mirascope `BaseMessageParam`.
        """
        converted: list[BaseMessageParam] = []
        for message_param in message_params:
            if isinstance(message_param, UserMessage):
                if isinstance(message_param.content, str):
                    converted.append(
                        BaseMessageParam(role="user", content=message_param.content)
                    )
                elif isinstance(message_param.content, list):
                    converted_parts = _parse_content(message_param.content)
                    converted.append(
                        BaseMessageParam(role="user", content=converted_parts)
                    )
            elif isinstance(message_param, AssistantMessage):
                converted_parts = []
                if tool_calls := message_param.tool_calls:
                    converted_parts.extend(
                        ToolCallPart(
                            type="tool_call",
                            name=tool_call.function.name,
                            id=tool_call.id,
                            args=json.loads(tool_call.function.arguments),
                        )
                        for tool_call in tool_calls
                    )
                if isinstance(message_param.content, str):
                    converted_parts.append(
                        TextPart(type="text", text=message_param.content)
                    )
                elif isinstance(message_param.content, list):
                    converted_parts = _parse_content(message_param.content)
                else:
                    converted_parts.append(TextPart(type="text", text=""))
                converted.append(
                    BaseMessageParam(
                        role="assistant",
                        content=converted_parts[0].text
                        if len(converted_parts) == 1
                        and isinstance(converted_parts[0], TextPart)
                        else converted_parts,
                    )
                )
            elif isinstance(message_param, ToolMessage):
                converted.append(
                    BaseMessageParam(
                        role="tool",
                        content=[
                            ToolResultPart(
                                type="tool_result",
                                name="",
                                content=message_param.content,
                                id=message_param.tool_call_id,
                                is_error=False,
                            )
                        ],
                    )
                )
        return converted
