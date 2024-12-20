import json

from azure.ai.inference.models import (
    AssistantMessage,
)

from mirascope.core import BaseMessageParam
from mirascope.core.base.message_param import ToolCallPart


def convert_message_param_to_base_message_param(
    message_param: AssistantMessage,
) -> BaseMessageParam:
    """Converts a Part to a BaseMessageParam."""
    role: str = "assistant"
    if not message_param.tool_calls:
        return BaseMessageParam(role=role, content=message_param.content or "")

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

    return BaseMessageParam(role="tool", content=contents)
