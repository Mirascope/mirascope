"""This module contains the OpenAIMessageParamConverter class."""

import json

from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
)

from mirascope.core import BaseMessageParam
from mirascope.core.base import TextPart, ToolCallPart
from mirascope.core.base._utils._base_message_param_converter import (
    BaseMessageParamConverter,
)
from mirascope.core.openai._utils import convert_message_params


class OpenAIMessageParamConverter(BaseMessageParamConverter):
    def to_provider(
        self, message_params: list[BaseMessageParam]
    ) -> list[ChatCompletionMessageParam]:
        """Converts base message params to OpenAI message params."""
        return convert_message_params(message_params)

    def from_provider(
        self, message_params: list[ChatCompletionAssistantMessageParam]
    ) -> list[BaseMessageParam]:
        """Converts OpenAI message params to base message params."""
        converted = []
        for message_param in message_params:
            contents = []
            role: str = "assistant"
            content = message_param.get("content")
            if isinstance(content, str):
                return BaseMessageParam(role=role, content=content)
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

            converted.append(BaseMessageParam(role=role, content=contents))
        return converted
