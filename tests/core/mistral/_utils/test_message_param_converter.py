import base64
import json
from unittest.mock import MagicMock

import pytest
from mistralai.models import (
    AssistantMessage,
    FunctionCall,
    ImageURL,
    ImageURLChunk,
    ReferenceChunk,
    TextChunk,
    ToolCall,
    ToolMessage,
)

from mirascope.core import BaseMessageParam
from mirascope.core.base import ImagePart, TextPart
from mirascope.core.base.message_param import ImageURLPart, ToolCallPart, ToolResultPart
from mirascope.core.mistral._utils._message_param_converter import (
    MistralMessageParamConverter,
)


def test_convert_with_string_content_no_tool_calls():
    message = MagicMock(spec=AssistantMessage)
    message.role = "assistant"
    message.content = "Hello world"
    message.tool_calls = None

    results = MistralMessageParamConverter.from_provider([message])
    assert len(results) == 1

    result = results[0]
    assert isinstance(result, BaseMessageParam)
    assert result.role == "assistant"
    assert result.content == "Hello world"


def test_convert_with_string_content_and_tool_calls():
    message = MagicMock(spec=AssistantMessage)
    message.role = "assistant"
    message.content = "Some text"
    tool_call = MagicMock()
    tool_call.function.name = "my_tool"
    tool_call.function.arguments = json.dumps({"arg": "val"})
    tool_call.id = "tool_call_id"
    message.tool_calls = [tool_call]

    results = MistralMessageParamConverter.from_provider([message])
    assert len(results) == 1
    assert results == [
        BaseMessageParam(
            role="tool",
            content=[
                ToolCallPart(
                    type="tool_call",
                    name="my_tool",
                    args={"arg": "val"},
                    id="tool_call_id",
                )
            ],
        ),
    ]


def test_convert_with_list_content_single_text_chunk():
    text_chunk = MagicMock(spec=TextChunk)
    text_chunk.text = "Single text chunk"
    message = MagicMock(spec=AssistantMessage)
    message.role = "assistant"
    message.content = [text_chunk]
    message.tool_calls = None

    results = MistralMessageParamConverter.from_provider([message])
    assert len(results) == 1

    result = results[0]
    assert result.role == "assistant"
    assert result.content == "Single text chunk"


def test_convert_with_list_content_multiple_text_chunks():
    text_chunk1 = MagicMock(spec=TextChunk)
    text_chunk1.text = "Hello"
    text_chunk2 = MagicMock(spec=TextChunk)
    text_chunk2.text = "World"
    message = MagicMock(spec=AssistantMessage)
    message.role = "assistant"
    message.content = [text_chunk1, text_chunk2]
    message.tool_calls = None

    results = MistralMessageParamConverter.from_provider([message])
    result = results[0]
    assert result.role == "assistant"
    assert len(result.content) == 2
    assert isinstance(result.content[0], TextPart)
    assert result.content[0].text == "Hello"


def test_convert_with_list_content_image_url_chunk_str():
    # Create a valid data URL
    mime_type = "image/png"
    image_data = b"fake_image_data"
    b64 = base64.b64encode(image_data).decode("utf-8")
    data_url = f"data:{mime_type};base64,{b64}"

    image_chunk = MagicMock(spec=ImageURLChunk)
    image_chunk.image_url = data_url
    message = MagicMock(spec=AssistantMessage)
    message.role = "assistant"
    message.content = [image_chunk]
    message.tool_calls = None

    results = MistralMessageParamConverter.from_provider([message])
    result = results[0]
    assert len(result.content) == 1
    assert isinstance(result.content[0], ImagePart)
    assert result.content[0].media_type == mime_type
    assert result.content[0].image == image_data


def test_convert_with_list_content_image_url():
    image_chunk = MagicMock(spec=ImageURLChunk)
    image_chunk.image_url = "https://example.com/image.jpg"
    message = MagicMock(spec=AssistantMessage)
    message.role = "assistant"
    message.content = [image_chunk]
    message.tool_calls = None

    assert MistralMessageParamConverter.from_provider([message]) == [
        BaseMessageParam(
            role="assistant",
            content=[
                ImageURLPart(
                    type="image_url", url="https://example.com/image.jpg", detail=None
                )
            ],
        ),
    ]


def test_convert_with_list_content_image_url_type_is_ImageURL():
    image_url = ImageURL(url="data:image/jpeg;base64,aW1hZ2U=")
    image_chunk = ImageURLChunk(image_url=image_url)
    message = MagicMock(spec=AssistantMessage)
    message.role = "assistant"
    message.content = [image_chunk]
    result = MistralMessageParamConverter.from_provider([message])
    assert len(result) == 1
    assert result == [
        BaseMessageParam(
            role="assistant",
            content=[
                ImagePart(
                    type="image", media_type="image/jpeg", image=b"image", detail=None
                )
            ],
        )
    ]


def test_convert_with_list_content_image_url_type_is_IageURL_url_valid():
    image_url = ImageURL(url="https://example.com/image.jpg")
    image_chunk = ImageURLChunk(image_url=image_url)
    message = MagicMock(spec=AssistantMessage)
    message.role = "assistant"
    message.content = [image_chunk]
    assert MistralMessageParamConverter.from_provider([message]) == [
        BaseMessageParam(
            role="assistant",
            content=[
                ImageURLPart(
                    type="image_url", url="https://example.com/image.jpg", detail=None
                )
            ],
        ),
    ]


def test_convert_with_list_content_reference_chunk():
    ref_chunk = MagicMock(spec=ReferenceChunk)
    message = MagicMock(spec=AssistantMessage)
    message.role = "assistant"
    message.content = [ref_chunk]
    message.tool_calls = None

    with pytest.raises(ValueError, match="ReferenceChunk is not supported"):
        MistralMessageParamConverter.from_provider([message])


def test_convert_with_list_content_unknown_chunk():
    class UnknownChunk:
        pass

    unknown_chunk = UnknownChunk()
    message = MagicMock(spec=AssistantMessage)
    message.role = "assistant"
    message.content = [unknown_chunk]
    message.tool_calls = None

    with pytest.raises(ValueError, match="Unsupported ContentChunk type: UnknownChunk"):
        MistralMessageParamConverter.from_provider([message])


def test_convert_with_tool_calls_arguments_as_str():
    tool_call = MagicMock()
    tool_call.function.name = "tool_json"
    tool_call.function.arguments = json.dumps({"x": 1})
    tool_call.id = "tc1"

    message = MagicMock(spec=AssistantMessage)
    message.role = "assistant"
    message.content = None
    message.tool_calls = [tool_call]

    results = MistralMessageParamConverter.from_provider([message])
    result = results[0]
    assert len(result.content) == 1
    assert isinstance(result.content[0], ToolCallPart)
    assert result.content[0].name == "tool_json"
    assert result.content[0].args == {"x": 1}
    assert result.content[0].id == "tc1"


def test_to_provider():
    message_param = BaseMessageParam(
        role="assistant",
        content=[
            TextPart(type="text", text="Hello"),
            ImagePart(
                type="image",
                media_type="image/jpeg",
                image=b"image",
                detail="auto",
            ),
            ToolCallPart(
                type="tool_call",
                name="tool_name",
                args={"arg": "val"},
                id="tool_id",
            ),
        ],
    )

    result = MistralMessageParamConverter.to_provider([message_param])
    assert len(result) == 1
    assert result == [
        AssistantMessage(
            content=[
                TextChunk(text="Hello", TYPE="text"),
                ImageURLChunk(
                    image_url=ImageURL(
                        url="data:image/jpeg;base64,aW1hZ2U=", detail="auto"
                    ),
                    TYPE="image_url",
                ),
            ],
            tool_calls=[
                ToolCall(
                    function=FunctionCall(name="tool_name", arguments={"arg": "val"}),
                    id="tool_id",
                    type="function",
                )
            ],
            prefix=False,
            role="assistant",
        )
    ]


def test_tool_message():
    result = MistralMessageParamConverter.from_provider(
        [
            ToolMessage(
                content="Hello", role="tool", name="tool_name", tool_call_id="tool_id"
            )
        ]
    )
    assert len(result) == 1
    assert result == [
        BaseMessageParam(
            role="tool",
            content=[
                ToolResultPart(
                    type="tool_result",
                    name="tool_name",
                    content="Hello",
                    id="tool_id",
                    is_error=False,
                )
            ],
        )
    ]


def test_tool_message_after_text():
    result = MistralMessageParamConverter.from_provider(
        [
            AssistantMessage(
                content="Hello",
            ),
            ToolMessage(
                content="Hello",
                role="tool",
                name="tool_name",
                tool_call_id="tool_id",
            ),
        ]
    )
    assert result == [
        BaseMessageParam(role="assistant", content="Hello"),
        BaseMessageParam(
            role="tool",
            content=[
                ToolResultPart(
                    type="tool_result",
                    name="tool_name",
                    content="Hello",
                    id="tool_id",
                    is_error=False,
                )
            ],
        ),
    ]
