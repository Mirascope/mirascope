import json

from groq.types.chat import ChatCompletionAssistantMessageParam

from mirascope.core import BaseMessageParam
from mirascope.core.base import TextPart
from mirascope.core.base.message_param import ToolCallPart
from mirascope.core.groq._utils._message_param_converter import (
    GroqMessageParamConverter,
)


def test_convert_with_only_content():
    """
    If there's only content string, role="assistant", content=that string.
    """
    message_param = ChatCompletionAssistantMessageParam(
        role="assistant", content="Hello world"
    )
    results = GroqMessageParamConverter.from_provider([message_param])
    assert len(results) == 1

    result = results[0]
    assert isinstance(result, BaseMessageParam)
    assert result.role == "assistant"
    assert result.content == "Hello world"


def test_convert_with_content_and_tool_calls():
    """
    If there's both content and tool_calls, final role="tool" and we
    have [TextPart, ToolCallPart].
    """
    message_param = ChatCompletionAssistantMessageParam(
        role="assistant",
        content="This is a message",
        tool_calls=[
            {
                "type": "function",
                "function": {
                    "name": "test_tool",
                    "arguments": json.dumps({"param": "value"}),
                },
                "id": "tool_call_123",
            }
        ],
    )
    results = GroqMessageParamConverter.from_provider([message_param])
    assert len(results) == 1

    result = results[0]
    assert isinstance(result, BaseMessageParam)
    assert result.role == "tool"
    assert len(result.content) == 2
    assert isinstance(result.content[0], TextPart)
    assert result.content[0].text == "This is a message"
    part = result.content[1]
    assert isinstance(part, ToolCallPart)
    assert part.name == "test_tool"
    assert part.args == {"param": "value"}
    assert part.id == "tool_call_123"


def test_convert_with_only_tool_calls():
    """
    If there's no content but tool_calls, we only get ToolCallParts in the final list.
    """
    message_param = ChatCompletionAssistantMessageParam(
        role="assistant",
        content=None,
        tool_calls=[
            {
                "type": "function",
                "function": {
                    "name": "some_tool",
                    "arguments": json.dumps({"key": "val"}),
                },
                "id": "tool_call_456",
            }
        ],
    )
    results = GroqMessageParamConverter.from_provider([message_param])
    assert len(results) == 1

    result = results[0]
    assert result.role == "tool"
    assert len(result.content) == 1
    part = result.content[0]
    assert isinstance(part, ToolCallPart)
    assert part.name == "some_tool"
    assert part.args == {"key": "val"}
    assert part.id == "tool_call_456"


def test_convert_with_no_content_no_tool_calls():
    """
    If there's no content or tool_calls, we might get role="tool" with empty content or role="assistant".
    Depends on your internal logic.
    """
    message_param = ChatCompletionAssistantMessageParam(
        role="assistant", content=None, tool_calls=[]
    )
    results = GroqMessageParamConverter.from_provider([message_param])
    assert len(results) == 1

    result = results[0]
    # Possibly result.role == "tool" if code says so, or "assistant"
    # We'll assume "tool" if your code sets that. Adjust as needed:
    assert result.role == "tool"
    assert result.content == []


def test_convert_base_message_param():
    """
    If there's a BaseMessageParam, we should get that as is.
    """
    message_param = BaseMessageParam(role="assistant", content="Hello world")
    results = GroqMessageParamConverter.to_provider([message_param])
    assert results == [
        ChatCompletionAssistantMessageParam(role="assistant", content="Hello world")
    ]
