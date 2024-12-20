from unittest.mock import MagicMock

from cohere.types import ChatMessage

from mirascope.core import BaseMessageParam
from mirascope.core.base import TextPart, ToolCallPart
from mirascope.core.cohere._utils._convert_message_param_to_base_message_param import (
    convert_message_param_to_base_message_param,
)


def test_no_tool_calls_with_message():
    """Covers the branch where no tool_calls are present and a message is provided."""
    message_param = MagicMock(spec=ChatMessage)
    message_param.tool_calls = None
    message_param.message = "Hello assistant"

    result = convert_message_param_to_base_message_param(message_param)
    assert isinstance(result, BaseMessageParam)
    assert result.role == "assistant"
    assert result.content == "Hello assistant"


def test_tool_calls_with_message():
    """Covers the branch where tool_calls are present and message is provided."""
    tool_call = MagicMock()
    tool_call.name = "test_tool"
    tool_call.parameters = {"arg": "value"}

    message_param = MagicMock(spec=ChatMessage)
    message_param.tool_calls = [tool_call]
    message_param.message = "Message before tool"

    result = convert_message_param_to_base_message_param(message_param)
    assert isinstance(result, BaseMessageParam)
    assert result.role == "tool"
    assert len(result.content) == 2
    assert isinstance(result.content[0], TextPart)
    assert result.content[0].text == "Message before tool"
    assert isinstance(result.content[1], ToolCallPart)
    assert result.content[1].name == "test_tool"
    assert result.content[1].args == {"arg": "value"}


def test_tool_calls_no_message():
    """Covers the branch where tool_calls are present but no message."""
    tool_call1 = MagicMock()
    tool_call1.name = "tool_one"
    tool_call1.parameters = {"param1": "val1"}

    tool_call2 = MagicMock()
    tool_call2.name = "tool_two"
    tool_call2.parameters = {"param2": "val2"}

    message_param = MagicMock(spec=ChatMessage)
    message_param.tool_calls = [tool_call1, tool_call2]
    message_param.message = None

    result = convert_message_param_to_base_message_param(message_param)
    assert isinstance(result, BaseMessageParam)
    assert result.role == "tool"
    # No message means no TextPart is added
    assert len(result.content) == 2
    assert isinstance(result.content[0], ToolCallPart)
    assert result.content[0].name == "tool_one"
    assert result.content[0].args == {"param1": "val1"}
    assert isinstance(result.content[1], ToolCallPart)
    assert result.content[1].name == "tool_two"
    assert result.content[1].args == {"param2": "val2"}
