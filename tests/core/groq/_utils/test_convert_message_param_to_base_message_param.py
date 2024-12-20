import json

from groq.types.chat import ChatCompletionAssistantMessageParam

from mirascope.core import BaseMessageParam
from mirascope.core.base import TextPart
from mirascope.core.base.message_param import ToolCallPart
from mirascope.core.groq._utils._convert_message_param_to_base_message_param import (
    convert_message_param_to_base_message_param,
)


def test_convert_with_only_content():
    """
    Test when message_param has only a content string and no tool_calls.
    Expected result: role="assistant", content is a string.
    """
    message_param = ChatCompletionAssistantMessageParam(content="Hello world")
    result = convert_message_param_to_base_message_param(message_param)
    assert isinstance(result, BaseMessageParam)
    assert result.role == "assistant"
    assert result.content == "Hello world"


def test_convert_with_content_and_tool_calls():
    """
    Test when message_param has both content and tool_calls.
    Expected result: role="tool", content is a list [TextPart, ToolCallPart].
    """
    message_param = ChatCompletionAssistantMessageParam(
        content="This is a message",
        tool_calls=[
            {
                "function": {
                    "name": "test_tool",
                    "arguments": json.dumps({"param": "value"}),
                },
                "id": "tool_call_123",
            }
        ],
    )
    result = convert_message_param_to_base_message_param(message_param)
    assert isinstance(result, BaseMessageParam)
    assert result.role == "tool"
    assert len(result.content) == 2
    assert isinstance(result.content[0], TextPart)
    assert result.content[0].text == "This is a message"
    assert isinstance(result.content[1], ToolCallPart)
    assert result.content[1].name == "test_tool"
    assert result.content[1].args == {"param": "value"}
    assert result.content[1].id == "tool_call_123"


def test_convert_with_only_tool_calls():
    """
    Test when message_param has no content but only tool_calls.
    Expected result: role="tool", content is a list containing only ToolCallParts.
    """
    message_param = ChatCompletionAssistantMessageParam(
        content=None,
        tool_calls=[
            {
                "function": {
                    "name": "some_tool",
                    "arguments": json.dumps({"key": "val"}),
                },
                "id": "tool_call_456",
            }
        ],
    )
    result = convert_message_param_to_base_message_param(message_param)
    assert isinstance(result, BaseMessageParam)
    assert result.role == "tool"
    assert len(result.content) == 1
    assert isinstance(result.content[0], ToolCallPart)
    assert result.content[0].name == "some_tool"
    assert result.content[0].args == {"key": "val"}
    assert result.content[0].id == "tool_call_456"


def test_convert_with_no_content_no_tool_calls():
    """
    Test when message_param has neither content nor tool_calls.
    Expected result: role="tool", content is an empty list.
    """
    message_param = ChatCompletionAssistantMessageParam(content=None, tool_calls=None)
    result = convert_message_param_to_base_message_param(message_param)
    assert isinstance(result, BaseMessageParam)
    assert result.role == "tool"
    assert result.content == []
