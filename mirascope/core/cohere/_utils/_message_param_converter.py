from typing import cast

from cohere.types import ChatMessage

from mirascope.core import BaseMessageParam
from mirascope.core.base import TextPart, ToolCallPart
from mirascope.core.base._utils._base_message_param_converter import (
    BaseMessageParamConverter,
)
from mirascope.core.cohere._utils import convert_message_params


class CohereMessageParamConverter(BaseMessageParamConverter):
    """Converts between Cohere `ChatMessage` and Mirascope `BaseMessageParam`."""

    @staticmethod
    def to_provider(message_params: list[BaseMessageParam]) -> list[ChatMessage]:
        """
        Convert from Mirascope `BaseMessageParam` to Cohere's `ChatMessage`.
        """
        return convert_message_params(
            cast(list[BaseMessageParam | ChatMessage], message_params)
        )

    @staticmethod
    def from_provider(message_params: list[ChatMessage]) -> list[BaseMessageParam]:
        """
        Convert from Cohere's `ChatMessage` to Mirascope `BaseMessageParam`.
        """
        converted = []
        for message_param in message_params:
            role = getattr(message_param, "role", "assistant")
            if not message_param.tool_calls:
                converted.append(
                    BaseMessageParam(role=role, content=message_param.message)
                )
                continue

            converted_content = []

            if message_param.message:
                converted_content.append(
                    TextPart(type="text", text=message_param.message)
                )

            for tool_call in message_param.tool_calls:
                converted_content.append(
                    ToolCallPart(
                        type="tool_call", name=tool_call.name, args=tool_call.parameters
                    )
                )

            converted.append(BaseMessageParam(role=role, content=converted_content))
        return converted
