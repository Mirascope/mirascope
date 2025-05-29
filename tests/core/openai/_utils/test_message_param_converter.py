import json

import pytest
from openai.types.chat import ChatCompletionAssistantMessageParam

from mirascope.core import BaseMessageParam
from mirascope.core.base import (
    AudioPart,
    ImageURLPart,
    TextPart,
    ToolCallPart,
)
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


def test_to_provider():
    message_param = BaseMessageParam(
        role="assistant",
        content=[
            TextPart(type="text", text="Hello, world!"),
            ToolCallPart(type="tool_call", name="test_tool", args={"key": "value"}),
            ToolCallPart(type="tool_call", name="test_tool_2", args={"key": "value"}),
        ],
    )
    results = OpenAIMessageParamConverter.to_provider([message_param])
    assert results == [
        {
            "content": [{"text": "Hello, world!", "type": "text"}],
            "role": "assistant",
            "tool_calls": [
                {
                    "function": {
                        "arguments": '{"key": "value"}',
                        "name": "test_tool",
                    },
                    "id": None,
                    "type": "function",
                },
                {
                    "function": {
                        "arguments": '{"key": "value"}',
                        "name": "test_tool_2",
                    },
                    "id": None,
                    "type": "function",
                },
            ],
        }
    ]


def test_convert_message_param_tool_result():
    message_param = ChatCompletionAssistantMessageParam(  # pyright: ignore [reportCallIssue]
        role="tool",
        name="test_tool",
        content="result",
        tool_call_id="tool_call_1",
    )
    results = OpenAIMessageParamConverter.from_provider([message_param])
    result = results[0]
    assert len(result.content) == 1
    assert result.content[0].name == "test_tool"  # pyright: ignore [reportAttributeAccessIssue]
    assert result.content[0].content == "result"  # pyright: ignore [reportAttributeAccessIssue]
    assert result.content[0].id == "tool_call_1"  # pyright: ignore [reportAttributeAccessIssue]
    assert not result.content[0].is_error  # pyright: ignore [reportAttributeAccessIssue]
    assert result.role == "tool"


def test_convert_message_param_list_content_with_image_url():
    message_param = ChatCompletionAssistantMessageParam(
        role="assistant",
        content=[
            {  # pyright: ignore [reportArgumentType]
                "type": "image_url",
                "image_url": {"url": "https://example.com/image", "detail": "custom"},
            }
        ],
    )
    results = OpenAIMessageParamConverter.from_provider([message_param])
    assert len(results) == 1
    result = results[0]
    assert isinstance(result.content, list)
    assert len(result.content) == 1
    part = result.content[0]
    assert isinstance(part, ImageURLPart)
    assert part.url == "https://example.com/image"
    assert part.detail == "custom"


def test_convert_message_param_list_content_with_input_audio():
    message_param = ChatCompletionAssistantMessageParam(
        role="assistant",
        content=[
            {  # pyright: ignore [reportArgumentType]
                "type": "input_audio",
                "input_audio": {"format": "mp3", "data": "YXVkaW8="},
            }
        ],
    )
    results = OpenAIMessageParamConverter.from_provider([message_param])
    assert len(results) == 1
    result = results[0]
    assert isinstance(result.content, list)
    assert len(result.content) == 1
    part = result.content[0]
    assert isinstance(part, AudioPart)
    assert part.media_type == "audio/mp3"
    assert part.audio == "YXVkaW8="
