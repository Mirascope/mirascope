from unittest.mock import MagicMock

from cohere.types import ChatMessage

from mirascope.core import BaseMessageParam
from mirascope.core.base import TextPart, ToolCallPart
from mirascope.core.cohere._utils._message_param_converter import (
    CohereMessageParamConverter,
)


def test_no_tool_calls_with_message():
    """
    If no tool_calls are present and there's a message, return role="assistant", content=string.
    """
    message_param = MagicMock(spec=ChatMessage)
    message_param.tool_calls = None
    message_param.message = "Hello assistant"

    results = CohereMessageParamConverter.from_provider([message_param])
    assert len(results) == 1

    result = results[0]
    assert isinstance(result, BaseMessageParam)
    assert result.role == "assistant"
    assert result.content == "Hello assistant"


def test_tool_calls_with_message():
    """
    If tool_calls are present and there's a message, we expect role="tool" with [TextPart, ToolCallPart].
    """
    tool_call = MagicMock()
    tool_call.name = "test_tool"
    tool_call.parameters = {"arg": "value"}

    message_param = MagicMock(spec=ChatMessage)
    message_param.tool_calls = [tool_call]
    message_param.message = "Message before tool"

    results = CohereMessageParamConverter.from_provider([message_param])
    assert len(results) == 1

    result = results[0]
    assert isinstance(result, BaseMessageParam)
    assert result.role == "assistant"
    assert len(result.content) == 2
    assert isinstance(result.content[0], TextPart)
    assert result.content[0].text == "Message before tool"
    part = result.content[1]
    assert isinstance(part, ToolCallPart)
    assert part.name == "test_tool"
    assert part.args == {"arg": "value"}


def test_tool_calls_no_message():
    """
    If tool_calls are present but no message, we get multiple ToolCallParts.
    """
    tool_call1 = MagicMock()
    tool_call1.name = "tool_one"
    tool_call1.parameters = {"param1": "val1"}

    tool_call2 = MagicMock()
    tool_call2.name = "tool_two"
    tool_call2.parameters = {"param2": "val2"}

    message_param = MagicMock(spec=ChatMessage)
    message_param.tool_calls = [tool_call1, tool_call2]
    message_param.message = None

    results = CohereMessageParamConverter.from_provider([message_param])
    assert len(results) == 1

    result = results[0]
    assert isinstance(result, BaseMessageParam)
    assert result.role == "assistant"
    assert len(result.content) == 2
    assert isinstance(result.content[0], ToolCallPart)
    assert result.content[0].name == "tool_one"
    assert result.content[0].args == {"param1": "val1"}
    assert isinstance(result.content[1], ToolCallPart)
    assert result.content[1].name == "tool_two"
    assert result.content[1].args == {"param2": "val2"}


def test_base_message_param_to_provider():
    """
    Test that `to_provider` method returns a list of ChatMessage objects.
    """
    message_param = BaseMessageParam(role="assistant", content="Hello world")
    results = CohereMessageParamConverter.to_provider([message_param])
    assert len(results) == 1

    result = results[0]
    assert isinstance(result, ChatMessage)
    assert result.message == "Hello world"
    assert result.tool_calls is None
