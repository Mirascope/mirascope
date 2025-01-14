import base64
import json
from unittest.mock import MagicMock

import pytest
from mistralai.models import AssistantMessage, ImageURLChunk, ReferenceChunk, TextChunk

from mirascope.core import BaseMessageParam
from mirascope.core.base import ImagePart, TextPart
from mirascope.core.base.message_param import ToolCallPart
from mirascope.core.mistral._utils._convert_message_param_to_base_message_param import (
    convert_message_param_to_base_message_param,
)


def test_convert_with_string_content_no_tool_calls():
    """
    Test when content is a string and no tool calls.
    This should produce one TextPart and return its content as a string.
    """
    message = MagicMock(spec=AssistantMessage)
    message.content = "Hello world"
    message.tool_calls = None

    result = convert_message_param_to_base_message_param(message)
    assert isinstance(result, BaseMessageParam)
    assert result.role == "assistant"
    assert result.content == "Hello world"


def test_convert_with_string_content_and_tool_calls():
    """
    Test when content is a string and there are tool calls.
    This should produce one TextPart + ToolCallPart(s), and return all as a list.
    Because multiple parts exist, we return a list instead of a single string.
    """
    message = MagicMock(spec=AssistantMessage)
    message.content = "Some text"
    # Mock a tool call
    tool_call = MagicMock()
    tool_call.function.name = "my_tool"
    tool_call.function.arguments = json.dumps({"arg": "val"})
    tool_call.id = "tool_call_id"
    message.tool_calls = [tool_call]

    result = convert_message_param_to_base_message_param(message)
    assert isinstance(result, BaseMessageParam)
    assert result.role == "assistant"
    assert len(result.content) == 2
    assert isinstance(result.content[0], TextPart)
    assert result.content[0].text == "Some text"
    assert isinstance(result.content[1], ToolCallPart)
    assert result.content[1].name == "my_tool"
    assert result.content[1].args == {"arg": "val"}
    assert result.content[1].id == "tool_call_id"


def test_convert_with_list_content_single_text_chunk():
    """
    Test when content is a list with a single TextChunk.
    With no tool calls, a single TextPart should return content as string.
    """
    text_chunk = MagicMock(spec=TextChunk)
    text_chunk.text = "Single text chunk"
    message = MagicMock(spec=AssistantMessage)
    message.content = [text_chunk]
    message.tool_calls = None

    result = convert_message_param_to_base_message_param(message)
    assert isinstance(result, BaseMessageParam)
    assert result.role == "assistant"
    # Only one TextPart leads to content being returned as a string
    assert result.content == "Single text chunk"


def test_convert_with_list_content_multiple_text_chunks():
    """
    Test when content is a list with multiple TextChunks.
    Should return multiple TextPart objects in a list.
    """
    text_chunk1 = MagicMock(spec=TextChunk)
    text_chunk1.text = "Hello"
    text_chunk2 = MagicMock(spec=TextChunk)
    text_chunk2.text = "World"
    message = MagicMock(spec=AssistantMessage)
    message.content = [text_chunk1, text_chunk2]
    message.tool_calls = None

    result = convert_message_param_to_base_message_param(message)
    assert isinstance(result, BaseMessageParam)
    assert result.role == "assistant"
    # Multiple text parts => list of TextParts
    assert len(result.content) == 2
    assert isinstance(result.content[0], TextPart)
    assert result.content[0].text == "Hello"
    assert isinstance(result.content[1], TextPart)
    assert result.content[1].text == "World"


def test_convert_with_list_content_image_url_chunk_str():
    """
    Test when content includes an ImageURLChunk with a data URL as a string.
    Should extract image data and return an ImagePart.
    """
    # Create a valid data URL
    mime_type = "image/png"
    image_data = b"fake_image_data"
    image_base64 = base64.b64encode(image_data).decode("utf-8")
    data_url = f"data:{mime_type};base64,{image_base64}"

    image_chunk = MagicMock(spec=ImageURLChunk)
    image_chunk.image_url = data_url
    message = MagicMock(spec=AssistantMessage)
    message.content = [image_chunk]
    message.tool_calls = None

    result = convert_message_param_to_base_message_param(message)
    assert isinstance(result, BaseMessageParam)
    assert result.role == "assistant"
    assert len(result.content) == 1
    assert isinstance(result.content[0], ImagePart)
    assert result.content[0].media_type == mime_type
    assert result.content[0].image == image_data


def test_convert_with_list_content_image_url_chunk_obj():
    """
    Test when ImageURLChunk has an image_url object with a url attribute.
    Should also decode the data URL and return ImagePart.
    """
    mime_type = "image/jpeg"
    image_data = b"another_fake_image_data"
    image_base64 = base64.b64encode(image_data).decode("utf-8")
    data_url = f"data:{mime_type};base64,{image_base64}"

    image_url_obj = MagicMock()
    image_url_obj.url = data_url

    image_chunk = MagicMock(spec=ImageURLChunk)
    image_chunk.image_url = image_url_obj
    message = MagicMock(spec=AssistantMessage)
    message.content = [image_chunk]
    message.tool_calls = None

    result = convert_message_param_to_base_message_param(message)
    assert isinstance(result, BaseMessageParam)
    assert len(result.content) == 1
    img_part = result.content[0]
    assert isinstance(img_part, ImagePart)
    assert img_part.media_type == mime_type
    assert img_part.image == image_data


def test_convert_with_list_content_image_url_chunk_invalid_data_url():
    """
    Test when ImageURLChunk has an invalid data URL that does not match the regex.
    Should raise ValueError.
    """
    image_chunk = MagicMock(spec=ImageURLChunk)
    image_chunk.image_url = "not_a_data_url"
    message = MagicMock(spec=AssistantMessage)
    message.content = [image_chunk]
    message.tool_calls = None

    with pytest.raises(
        ValueError,
        match="ImageURLChunk image_url is not in a supported data URL format.",
    ):
        convert_message_param_to_base_message_param(message)


def test_convert_with_list_content_reference_chunk():
    """
    Test when there is a ReferenceChunk in the content.
    Should raise ValueError as it's not supported.
    """
    ref_chunk = MagicMock(spec=ReferenceChunk)
    message = MagicMock(spec=AssistantMessage)
    message.content = [ref_chunk]
    message.tool_calls = None

    with pytest.raises(
        ValueError,
        match="ReferenceChunk is not supported for conversion to BaseMessageParam.",
    ):
        convert_message_param_to_base_message_param(message)


def test_convert_with_list_content_unknown_chunk():
    """
    Test with a chunk type that is not TextChunk, ImageURLChunk, or ReferenceChunk.
    Should raise ValueError.
    """

    class UnknownChunk:
        pass

    unknown_chunk = UnknownChunk()
    message = MagicMock(spec=AssistantMessage)
    message.content = [unknown_chunk]
    message.tool_calls = None

    with pytest.raises(ValueError, match="Unsupported ContentChunk type: UnknownChunk"):
        convert_message_param_to_base_message_param(message)


def test_convert_with_tool_calls_arguments_as_str():
    """
    Test tool calls when arguments are a JSON string.
    """
    tool_call = MagicMock()
    tool_call.function.name = "tool_json"
    tool_call.function.arguments = json.dumps({"x": 1})
    tool_call.id = "tc1"
    message = MagicMock(spec=AssistantMessage)
    message.content = None  # no content
    message.tool_calls = [tool_call]

    result = convert_message_param_to_base_message_param(message)
    assert isinstance(result, BaseMessageParam)
    assert len(result.content) == 1
    assert isinstance(result.content[0], ToolCallPart)
    assert result.content[0].name == "tool_json"
    assert result.content[0].args == {"x": 1}
    assert result.content[0].id == "tc1"


def test_convert_with_tool_calls_arguments_as_dict():
    """
    Test tool calls when arguments are already a dict (not a string).
    """
    tool_call = MagicMock()
    tool_call.function.name = "tool_dict"
    tool_call.function.arguments = {"key": "value"}
    tool_call.id = "tc2"
    message = MagicMock(spec=AssistantMessage)
    message.content = "text before tool"
    message.tool_calls = [tool_call]

    # Here we have a text part and a tool call.
    # Multiple parts -> list of parts, not a single string.
    result = convert_message_param_to_base_message_param(message)
    assert isinstance(result, BaseMessageParam)
    assert len(result.content) == 2
    assert isinstance(result.content[0], TextPart)
    assert result.content[0].text == "text before tool"
    assert isinstance(result.content[1], ToolCallPart)
    assert result.content[1].name == "tool_dict"
    assert result.content[1].args == {"key": "value"}
    assert result.content[1].id == "tc2"
    assert result.role == "assistant"


def test_convert_with_empty_list_content_no_tool_calls():
    """
    Test when content is an empty list and no tool calls.
    Should return an empty list as content.
    """
    message = MagicMock(spec=AssistantMessage)
    message.content = []
    message.tool_calls = None

    result = convert_message_param_to_base_message_param(message)
    assert isinstance(result, BaseMessageParam)
    assert result.role == "assistant"
    # empty list of parts
    assert result.content == []


def test_image_url_object_valid_data_url() -> None:
    """Covers the 'else' branch with a valid data URL in image_url.url."""
    mime_type = "image/jpeg"
    image_data = b"fake_image_data"
    image_base64 = base64.b64encode(image_data).decode("utf-8")
    data_url = f"data:{mime_type};base64,{image_base64}"

    # Mock the image_url object
    image_url_obj = MagicMock()
    image_url_obj.url = data_url

    # Mock the ImageURLChunk
    chunk = MagicMock(spec=ImageURLChunk)
    chunk.image_url = image_url_obj

    message = MagicMock(spec=AssistantMessage)
    message.content = [chunk]
    message.tool_calls = None

    result = convert_message_param_to_base_message_param(message)
    assert isinstance(result, BaseMessageParam)
    assert len(result.content) == 1
    assert isinstance(result.content[0], ImagePart)
    assert result.content[0].media_type == mime_type
    assert result.content[0].image == image_data


def test_image_url_object_invalid_data_url() -> None:
    """Covers the 'else' branch with an invalid data URL in image_url.url to raise ValueError."""
    image_url_obj = MagicMock()
    image_url_obj.url = "not_a_data_url"

    chunk = MagicMock(spec=ImageURLChunk)
    chunk.image_url = image_url_obj

    message = MagicMock(spec=AssistantMessage)
    message.content = [chunk]
    message.tool_calls = None

    with pytest.raises(
        ValueError,
        match="ImageURLChunk image_url is not in a supported data URL format.",
    ):
        convert_message_param_to_base_message_param(message)
