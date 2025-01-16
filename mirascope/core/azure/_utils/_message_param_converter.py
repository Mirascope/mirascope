import json
from typing import cast

from azure.ai.inference.models import (
    AssistantMessage,
    ChatRequestMessage,
)

from mirascope.core import BaseMessageParam
from mirascope.core.azure._utils import convert_message_params
from mirascope.core.base._utils._base_message_param_converter import (
    BaseMessageParamConverter,
)
from mirascope.core.base.message_param import ToolCallPart


class AzureMessageParamConverter(BaseMessageParamConverter):
    """Converts between Azure `ChatRequestMessage` / `AssistantMessage` and Mirascope `BaseMessageParam`."""

    @staticmethod
    def to_provider(message_params: list[BaseMessageParam]) -> list[ChatRequestMessage]:
        """
        Convert from Mirascope `BaseMessageParam` to Azure's `ChatRequestMessage`.
        """
        return convert_message_params(
            cast(list[BaseMessageParam | ChatRequestMessage], message_params)
        )

    @staticmethod
    def from_provider(message_params: list[AssistantMessage]) -> list[BaseMessageParam]:
        """
        Convert from Azure's `AssistantMessage` back to Mirascope `BaseMessageParam`.
        """
        converted: list[BaseMessageParam] = []
        for message_param in message_params:
            role: str = "assistant"
            if not message_param.tool_calls:
                converted.append(
                    BaseMessageParam(role=role, content=message_param.content or "")
                )
                continue

            contents = []
            if tool_calls := message_param.tool_calls:
                for tool_call in tool_calls:
                    contents.append(
                        ToolCallPart(
                            type="tool_call",
                            name=tool_call.function.name,
                            id=tool_call.id,
                            args=json.loads(tool_call.function.arguments),
                        )
                    )

            converted.append(BaseMessageParam(role="tool", content=contents))
        return converted
