"""This module contains the OpenAIMessageParamConverter class."""

import json
from typing import cast

from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
)

from mirascope.core import BaseMessageParam
from mirascope.core.base import TextPart, ToolCallPart, ToolResultPart
from mirascope.core.base._utils._base_message_param_converter import (
    BaseMessageParamConverter,
)
from mirascope.core.openai._utils import convert_message_params


class OpenAIMessageParamConverter(BaseMessageParamConverter):
    @staticmethod
    def to_provider(
        message_params: list[BaseMessageParam],
    ) -> list[ChatCompletionMessageParam]:
        """Converts base message params to OpenAI message params."""
        return convert_message_params(
            cast(list[BaseMessageParam | ChatCompletionMessageParam], message_params)
        )

    @staticmethod
    def from_provider(
        message_params: list[ChatCompletionAssistantMessageParam],
    ) -> list[BaseMessageParam]:
        """Converts OpenAI message params to base message params."""
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
                                name=message_param["name"],
                                content=message_param["content"],
                                id=message_param["tool_call_id"],
                                is_error=False,
                            )
                        ],
                    )
                )
                continue
            elif isinstance(content, str):
                converted.append(
                    BaseMessageParam(role=message_param["role"], content=content)
                )
                continue
            elif isinstance(content, list):
                for part in content:
                    if "text" in part:
                        contents.append(TextPart(type="text", text=part["text"]))
                    else:
                        raise ValueError(part["refusal"])
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
            if contents:
                converted.append(
                    BaseMessageParam(role=message_param["role"], content=contents)
                )
        return converted
