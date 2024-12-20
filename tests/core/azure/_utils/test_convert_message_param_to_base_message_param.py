import json
from unittest.mock import MagicMock

from mirascope.core import BaseMessageParam
from mirascope.core.azure._utils._convert_message_param_to_base_message_param import (
    convert_message_param_to_base_message_param,
)
from mirascope.core.base.message_param import ToolCallPart


def test_convert_no_tool_calls_with_content():
    """
    Test when there are no tool_calls and content is present.
    Expect role="assistant" and content as the message_param.content string.
    """
    message_param = MagicMock()
    message_param.tool_calls = None
    message_param.content = "Hello Azure"

    result = convert_message_param_to_base_message_param(message_param)
    assert isinstance(result, BaseMessageParam)
    assert result.role == "assistant"
    assert result.content == "Hello Azure"


def test_convert_no_tool_calls_no_content():
    """
    Test when there are no tool_calls and no content.
    Expect role="assistant" and content to be an empty string.
    """
    message_param = MagicMock()
    message_param.tool_calls = None
    message_param.content = None  # or ""

    result = convert_message_param_to_base_message_param(message_param)
    assert isinstance(result, BaseMessageParam)
    assert result.role == "assistant"
    assert result.content == ""


def test_convert_with_single_tool_call():
    """
    Test when there is a single tool_call.
    Expect role="tool" and a single ToolCallPart in content.
    """
    # Mock the tool_call
    function = MagicMock()
    function.name = "test_tool"
    function.arguments = json.dumps({"param": "value"})

    tool_call = MagicMock()
    tool_call.id = "tool_call_1"
    tool_call.function = function

    message_param = MagicMock()
    message_param.tool_calls = [tool_call]
    message_param.content = "This content should be ignored because tool_calls exist."

    result = convert_message_param_to_base_message_param(message_param)
    assert isinstance(result, BaseMessageParam)
    assert result.role == "tool"
    assert len(result.content) == 1
    assert isinstance(result.content[0], ToolCallPart)
    assert result.content[0].name == "test_tool"
    assert result.content[0].args == {"param": "value"}
    assert result.content[0].id == "tool_call_1"


def test_convert_with_multiple_tool_calls():
    """
    Test when there are multiple tool_calls.
    Expect role="tool" and multiple ToolCallParts in content.
    """
    # Mock first tool_call
    function1 = MagicMock()
    function1.name = "tool_one"
    function1.arguments = json.dumps({"key1": "val1"})

    tool_call1 = MagicMock()
    tool_call1.id = "tc_1"
    tool_call1.function = function1

    # Mock second tool_call
    function2 = MagicMock()
    function2.name = "tool_two"
    function2.arguments = json.dumps({"key2": "val2"})

    tool_call2 = MagicMock()
    tool_call2.id = "tc_2"
    tool_call2.function = function2

    message_param = MagicMock()
    message_param.tool_calls = [tool_call1, tool_call2]
    message_param.content = "Ignored content"

    result = convert_message_param_to_base_message_param(message_param)
    assert isinstance(result, BaseMessageParam)
    assert result.role == "tool"
    assert len(result.content) == 2
    assert isinstance(result.content[0], ToolCallPart)
    assert result.content[0].name == "tool_one"
    assert result.content[0].args == {"key1": "val1"}
    assert result.content[0].id == "tc_1"

    assert isinstance(result.content[1], ToolCallPart)
    assert result.content[1].name == "tool_two"
    assert result.content[1].args == {"key2": "val2"}
    assert result.content[1].id == "tc_2"
