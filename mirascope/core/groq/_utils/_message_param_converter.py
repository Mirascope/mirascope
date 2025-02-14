import json
from typing import cast

from groq.types.chat import ChatCompletionMessageParam

from mirascope.core import BaseMessageParam
from mirascope.core.base import TextPart, ToolResultPart
from mirascope.core.base._utils._base_message_param_converter import (
    BaseMessageParamConverter,
)
from mirascope.core.base.message_param import ImageURLPart, ToolCallPart
from mirascope.core.groq._utils import convert_message_params


class GroqMessageParamConverter(BaseMessageParamConverter):
    """Converts between Groq `ChatCompletionMessageParam` and Mirascope `BaseMessageParam`."""

    @staticmethod
    def to_provider(
        message_params: list[BaseMessageParam],
    ) -> list[ChatCompletionMessageParam]:
        """
        Convert from Mirascope `BaseMessageParam` to Groq `ChatCompletionMessageParam`.
        """
        return convert_message_params(
            cast(list[BaseMessageParam | ChatCompletionMessageParam], message_params)
        )

    @staticmethod
    def from_provider(
        message_params: list[ChatCompletionMessageParam],
    ) -> list[BaseMessageParam]:
        """Convert from Groq's `ChatCompletionAssistantMessageParam` to Mirascope `BaseMessageParam`."""
        converted = []
        for message_param in message_params:
            contents = []
            content = message_param.get("content")
            if message_param["role"] == "tool":
                converted.append(
                    BaseMessageParam(
                        role="tool",
                        content=[
                            ToolResultPart(
                                type="tool_result",
                                name=getattr(message_param, "name", ""),
                                content=message_param["content"],
                                id=message_param["tool_call_id"],
                                is_error=False,
                            )
                        ],
                    )
                )
                continue
            if tool_calls := message_param.get("tool_calls"):
                for tool_call in tool_calls:
                    contents.append(
                        ToolCallPart(
                            type="tool_call",
                            name=tool_call["function"]["name"],
                            id=tool_call["id"],
                            args=json.loads(tool_call["function"]["arguments"]),
                        )
                    )
            elif isinstance(content, str):
                converted.append(
                    BaseMessageParam(role=message_param["role"], content=content)
                )
                continue
            elif isinstance(content, list):
                for part in content:
                    if "text" in part:
                        contents.append(TextPart(type="text", text=part["text"]))
                    elif "image_url" in part:
                        contents.append(
                            ImageURLPart(
                                type="image_url",
                                url=part["image_url"]["url"],
                                detail=part["image_url"].get("detail"),
                            )
                        )
            if contents:
                converted.append(
                    BaseMessageParam(role=message_param["role"], content=contents)
                )
            else:
                converted.append(
                    BaseMessageParam(role=message_param["role"], content="")
                )
        return converted
