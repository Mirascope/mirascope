import json
from typing import cast

from azure.ai.inference.models import (
    AssistantMessage,
    ChatRequestMessage,
    TextContentItem,
    ToolMessage,
    UserMessage,
)

from mirascope.core.azure._utils import convert_message_params
from mirascope.core.base import BaseMessageParam, TextPart, ToolCallPart, ToolResultPart
from mirascope.core.base._utils._base_message_param_converter import (
    BaseMessageParamConverter,
)


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
                    converted_parts = []
                    for part in message_param.content:
                        if isinstance(part, TextContentItem):
                            converted_parts.append(
                                TextPart(type="text", text=part.text)
                            )
                        # TODO: add support for image and audio parts here
                    converted.append(
                        BaseMessageParam(role="user", content=converted_parts)
                    )
            elif isinstance(message_param, AssistantMessage):
                if tool_calls := message_param.tool_calls:
                    content = [
                        ToolCallPart(
                            type="tool_call",
                            name=tool_call.function.name,
                            id=tool_call.id,
                            args=json.loads(tool_call.function.arguments),
                        )
                        for tool_call in tool_calls
                    ]
                else:
                    content = message_param.content or ""
                converted.append(BaseMessageParam(role="assistant", content=content))
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
