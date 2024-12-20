from cohere.types import (
    ChatMessage,
)

from mirascope.core import BaseMessageParam
from mirascope.core.base import TextPart, ToolCallPart


def convert_message_param_to_base_message_param(
    message_param: ChatMessage,
) -> BaseMessageParam:
    """Converts a Part to a BaseMessageParam."""

    if not message_param.tool_calls:
        return BaseMessageParam(role="assistant", content=message_param.message)

    converted_content = []

    if message_param.message:
        converted_content.append(TextPart(type="text", text=message_param.message))

    for tool_call in message_param.tool_calls:
        converted_content.append(
            ToolCallPart(
                type="tool_call", name=tool_call.name, args=tool_call.parameters
            )
        )

    return BaseMessageParam(role="tool", content=converted_content)
