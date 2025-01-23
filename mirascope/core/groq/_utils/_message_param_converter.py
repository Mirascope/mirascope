import json
from typing import cast

from groq.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
)

from mirascope.core import BaseMessageParam
from mirascope.core.base import TextPart
from mirascope.core.base._utils._base_message_param_converter import (
    BaseMessageParamConverter,
)
from mirascope.core.base.message_param import ToolCallPart
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
        message_params: list[ChatCompletionAssistantMessageParam],
    ) -> list[BaseMessageParam]:
        """
        Convert from Groq's `ChatCompletionAssistantMessageParam` to Mirascope `BaseMessageParam`.
        """
        converted = []
        for message_param in message_params:
            contents = []
            if (content := message_param.get("content")) and content is not None:
                contents.append(TextPart(text=content, type="text"))
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
            if len(contents) == 1 and isinstance(contents[0], TextPart):
                converted.append(
                    BaseMessageParam(role="assistant", content=contents[0].text)
                )
            else:
                converted.append(BaseMessageParam(role="tool", content=contents))
        return converted
