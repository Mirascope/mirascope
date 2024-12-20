import json

from groq.types.chat import (
    ChatCompletionAssistantMessageParam,
)

from mirascope.core import BaseMessageParam
from mirascope.core.base import TextPart
from mirascope.core.base.message_param import ToolCallPart


def convert_message_param_to_base_message_param(
    message_param: ChatCompletionAssistantMessageParam,
) -> BaseMessageParam:
    """Converts a message_param to a BaseMessageParam."""

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
        return BaseMessageParam(role="assistant", content=contents[0].text)
    return BaseMessageParam(role="tool", content=contents)
