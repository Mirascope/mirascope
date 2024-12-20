import json

from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
)

from ...base import BaseMessageParam, TextPart, ToolCallPart


def convert_message_param_to_base_message_param(
    message_param: ChatCompletionAssistantMessageParam,
) -> BaseMessageParam:
    """
    Convert AssistantMessageContent (str or List[ContentChunk]) into BaseMessageParam.
    """
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

    return BaseMessageParam(role=role, content=contents)
