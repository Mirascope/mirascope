import json

import pytest
from openai.types.chat import ChatCompletionAssistantMessageParam

from mirascope.core import BaseMessageParam
from mirascope.core.base import TextPart, ToolCallPart
from mirascope.core.openai._utils._message_param_converter import (
    OpenAIMessageParamConverter,
)


def test_convert_message_param_str_content():
    """
    If content is a string, produce role="assistant" with that string as content.
    """
    message_param = ChatCompletionAssistantMessageParam(
        role="assistant", content="Hello, world!"
    )
    results = OpenAIMessageParamConverter.from_provider([message_param])
    assert len(results) == 1

    result = results[0]
    assert isinstance(result, BaseMessageParam)
    assert result.role == "assistant"
    assert result.content == "Hello, world!"


def test_convert_message_param_list_content_with_text():
    """
    If content is a list of text blocks, produce multiple TextParts.
    """
    message_param = ChatCompletionAssistantMessageParam(
        role="assistant",
        content=[{"text": "Hello", "type": "text"}, {"text": "World", "type": "text"}],
    )
    results = OpenAIMessageParamConverter.from_provider([message_param])
    assert len(results) == 1

    result = results[0]
    assert len(result.content) == 2
    assert isinstance(result.content[0], TextPart)
    assert result.content[0].text == "Hello"


def test_convert_message_param_list_content_with_refusal():
    message_param = ChatCompletionAssistantMessageParam(
        role="assistant",
        content=[{"refusal": "I cannot do that", "type": "refusal"}],
    )
    with pytest.raises(ValueError, match="I cannot do that"):
        OpenAIMessageParamConverter.from_provider([message_param])


def test_convert_message_param_tool_calls():
    message_param = ChatCompletionAssistantMessageParam(
        role="assistant",
        content=[{"type": "text", "text": "Some content"}],
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
    results = OpenAIMessageParamConverter.from_provider([message_param])
    result = results[0]
    assert len(result.content) == 2
    assert isinstance(result.content[1], ToolCallPart)


def test_convert_message_param_no_content_no_tool_calls():
    message_param = ChatCompletionAssistantMessageParam(role="assistant", content=None)
    results = OpenAIMessageParamConverter.from_provider([message_param])
    assert not results
