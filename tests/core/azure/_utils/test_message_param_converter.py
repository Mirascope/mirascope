import json
from unittest.mock import MagicMock

from azure.ai.inference.models import (
    AssistantMessage,
    ImageContentItem,
    ImageUrl,
    TextContentItem,
    ToolMessage,
    UserMessage,
)

from mirascope.core import BaseMessageParam
from mirascope.core.azure._utils._message_param_converter import (
    AzureMessageParamConverter,
)
from mirascope.core.base import ImageURLPart
from mirascope.core.base.message_param import TextPart, ToolCallPart, ToolResultPart


def test_convert_no_tool_calls_with_content():
    """
    If there are no tool_calls and content is present, we expect a single BaseMessageParam
    with role="assistant" and content as a string.
    """
    message_param = MagicMock(spec=AssistantMessage)
    message_param.tool_calls = None
    message_param.content = "Hello Azure"

    results = AzureMessageParamConverter.from_provider([message_param])
    assert len(results) == 1

    result = results[0]
    assert isinstance(result, BaseMessageParam)
    assert result.role == "assistant"
    assert result.content == "Hello Azure"


def test_convert_content_list():
    """Test that we can convert a list of content parts properly."""
    message_param = MagicMock(spec=AssistantMessage)
    message_param.tool_calls = None
    message_param.content = [
        TextContentItem(text="Content 1"),
        TextContentItem(text="Content 2"),
        ImageContentItem(image_url=ImageUrl(url="https://example.com/image.jpg")),
    ]

    results = AzureMessageParamConverter.from_provider([message_param])
    assert len(results) == 1

    result = results[0]
    assert result.role == "assistant"
    assert len(result.content) == 3
    assert result.content[0] == TextPart(type="text", text="Content 1")
    assert result.content[1] == TextPart(type="text", text="Content 2")
    assert result.content[2] == ImageURLPart(
        type="image_url", url="https://example.com/image.jpg", detail=None
    )

    message_param = MagicMock(spec=UserMessage)
    message_param.tool_calls = None
    message_param.content = [
        TextContentItem(text="Content 1"),
        TextContentItem(text="Content 2"),
        ImageContentItem(image_url=ImageUrl(url="https://example.com/image.jpg")),
    ]

    results = AzureMessageParamConverter.from_provider([message_param])
    assert len(results) == 1

    result = results[0]
    assert result.role == "user"
    assert len(result.content) == 3
    assert result.content[0] == TextPart(type="text", text="Content 1")
    assert result.content[1] == TextPart(type="text", text="Content 2")
    assert result.content[2] == ImageURLPart(
        type="image_url", url="https://example.com/image.jpg", detail=None
    )


def test_convert_no_tool_calls_no_content():
    """
    If there are no tool_calls and no content, expect a single BaseMessageParam
    with role="assistant" and empty string content.
    """
    message_param = MagicMock(spec=AssistantMessage)
    message_param.tool_calls = None
    message_param.content = None  # or ""

    results = AzureMessageParamConverter.from_provider([message_param])
    assert len(results) == 1

    result = results[0]
    assert isinstance(result, BaseMessageParam)
    assert result.role == "assistant"
    assert result.content == ""


def test_convert_with_single_tool_call():
    """
    If there is a single tool_call, we expect role="tool" and a single ToolCallPart.
    """
    function = MagicMock()
    function.name = "test_tool"
    function.arguments = json.dumps({"param": "value"})

    tool_call = MagicMock()
    tool_call.id = "tool_call_1"
    tool_call.function = function

    message_param = MagicMock(spec=AssistantMessage)
    message_param.tool_calls = [tool_call]
    message_param.content = "Content should be ignored because of tool_calls"

    results = AzureMessageParamConverter.from_provider([message_param])
    assert len(results) == 1

    result = results[0]
    assert isinstance(result, BaseMessageParam)
    assert result.role == "assistant"
    assert len(result.content) == 2
    part = result.content[0]
    assert isinstance(part, ToolCallPart)
    assert part.name == "test_tool"
    assert part.args == {"param": "value"}
    assert part.id == "tool_call_1"


def test_convert_with_multiple_tool_calls():
    """
    If there are multiple tool_calls, expect role="tool" and multiple ToolCallParts.
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

    message_param = MagicMock(spec=AssistantMessage)
    message_param.tool_calls = [tool_call1, tool_call2]
    message_param.content = "Ignored content"

    results = AzureMessageParamConverter.from_provider([message_param])
    assert len(results) == 1

    result = results[0]
    assert isinstance(result, BaseMessageParam)
    assert result.role == "assistant"
    assert len(result.content) == 3

    part1 = result.content[0]
    assert isinstance(part1, ToolCallPart)
    assert part1.name == "tool_one"
    assert part1.args == {"key1": "val1"}
    assert part1.id == "tc_1"

    part2 = result.content[1]
    assert isinstance(part2, ToolCallPart)
    assert part2.name == "tool_two"
    assert part2.args == {"key2": "val2"}
    assert part2.id == "tc_2"


def test_convert_tool_message_param():
    """Tests converting a message parameter with the tool role."""
    message_param = MagicMock(spec=ToolMessage)
    message_param.role = "tool"
    message_param.content = "Message before tool"
    message_param.tool_call_id = "id"

    results = AzureMessageParamConverter.from_provider([message_param])
    assert len(results) == 1

    result = results[0]
    assert isinstance(result, BaseMessageParam)
    assert result.role == "tool"
    assert len(result.content) == 1
    assert result.content[0] == ToolResultPart(
        type="tool_result",
        name="",
        content="Message before tool",
        id="id",
        is_error=False,
    )


def test_base_message_param_to_provider():
    """
    If we have a BaseMessageParam, we should be able to convert it to AzureMessageParam.
    """
    message_param = BaseMessageParam(role="user", content="Hello Azure")
    results = AzureMessageParamConverter.to_provider([message_param])
    assert results == [{"role": "user", "content": "Hello Azure"}]


def test_empty_base_message_param_to_provider():
    """
    If we have an empty BaseMessageParam, we should get an empty list.
    """
    results = AzureMessageParamConverter.to_provider([])
    assert results == []
