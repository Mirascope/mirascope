import json

import pytest
from openai.types.chat import ChatCompletionAssistantMessageParam

from mirascope.core import BaseMessageParam
from mirascope.core.base import TextPart, ToolCallPart
from mirascope.core.openai._utils._convert_message_param_to_base_message_param import (
    convert_message_param_to_base_message_param,
)


def test_convert_message_param_str_content():
    """
    Test when content is a string.
    This covers the branch:
    if isinstance(content, str):
        return BaseMessageParam(role=role, content=content)
    """
    message_param = ChatCompletionAssistantMessageParam(
        role="assistant", content="Hello, world!"
    )
    result = convert_message_param_to_base_message_param(message_param)
    assert isinstance(result, BaseMessageParam)
    assert result.content == "Hello, world!"


def test_convert_message_param_list_content_with_text():
    """
    Test when content is a list and each part has 'text'.
    This covers the branch where 'text' in part leads to appending BaseMessageParam.
    """
    message_param = ChatCompletionAssistantMessageParam(
        role="assistant",
        content=[{"text": "Hello", "type": "text"}, {"text": "World", "type": "text"}],
    )
    result = convert_message_param_to_base_message_param(message_param)
    assert isinstance(result, BaseMessageParam)
    assert len(result.content) == 2
    assert result.content[0] == TextPart(type="text", text="Hello")
    assert result.content[1] == TextPart(type="text", text="World")


def test_convert_message_param_list_content_with_refusal():
    """
    Test when content is a list and a part lacks 'text', causing a ValueError.
    This covers the else branch:
    else:
        raise ValueError(part["refusal"])
    """
    message_param = ChatCompletionAssistantMessageParam(
        role="assistant",
        content=[{"refusal": "I cannot process this.", "type": "refusal"}],
    )
    with pytest.raises(ValueError, match="I cannot process this."):
        convert_message_param_to_base_message_param(message_param)


def test_convert_message_param_tool_calls():
    """
    Test when tool_calls are present.
    This covers the branch where tool_calls are appended as ToolCallPart.
    """
    message_param = ChatCompletionAssistantMessageParam(
        role="assistant",
        content=[{"text": "Some content"}],
        tool_calls=[
            {
                "type": "function",
                "function": {
                    "name": "test_tool",
                    "arguments": json.dumps({"key": "value"}),
                },
                "id": "tool_call_1",
            }
        ],
    )
    result = convert_message_param_to_base_message_param(message_param)
    assert isinstance(result, BaseMessageParam)
    assert len(result.content) == 2  # one from text, one from tool_call
    assert isinstance(result.content[1], ToolCallPart)
    assert result.content[1].name == "test_tool"
    assert result.content[1].args == {"key": "value"}
    assert result.content[1].id == "tool_call_1"


def test_convert_message_param_no_content_no_tool_calls():
    """
    Test when content is None and no tool_calls provided.
    Covers the scenario returning empty contents at the end.
    """
    message_param = ChatCompletionAssistantMessageParam(role="assistant", content=None)
    result = convert_message_param_to_base_message_param(message_param)
    assert isinstance(result, BaseMessageParam)
    assert result.content == []
