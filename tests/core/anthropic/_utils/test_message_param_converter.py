import base64
from io import BytesIO
from os import PathLike
from unittest.mock import mock_open, patch

import pytest

from mirascope.core import BaseMessageParam
from mirascope.core.anthropic._utils._message_param_converter import (
    AnthropicMessageParamConverter,
)
from mirascope.core.base import ImagePart, TextPart, ToolCallPart


def test_content_is_string():
    """
    If content is a simple string, `AnthropicMessageParamConverter.from_provider(...)`
    should produce a single `BaseMessageParam` with role="assistant".
    """
    message_param = {"content": "Hello string content", "role": "assistant"}
    results = AnthropicMessageParamConverter.from_provider(
        [message_param]
    )  # Note: returns list
    assert isinstance(results, list)
    assert len(results) == 1

    result = results[0]
    assert isinstance(result, BaseMessageParam)
    assert result.role == "assistant"
    assert result.content == "Hello string content"


def test_content_none():
    """
    If content is empty or None, treat as an empty list (or assistant with no content).
    """
    message_param = {"content": []}  # or None if your converter expects that
    results = AnthropicMessageParamConverter.from_provider([message_param])
    assert isinstance(results, list)
    assert len(results) == 1

    result = results[0]
    assert isinstance(result, BaseMessageParam)
    assert result.role == "assistant"
    assert result.content == []


def test_content_list_with_non_dict():
    """
    If the content is a list and some items are not dicts, skip them
    and only process valid dict blocks.
    """
    message_param = {
        "content": ["not a dict", {"type": "text", "text": "A valid text block"}]
    }
    results = AnthropicMessageParamConverter.from_provider([message_param])
    assert len(results) == 1

    result = results[0]
    assert result.role == "assistant"
    assert len(result.content) == 1
    assert isinstance(result.content[0], TextPart)
    assert result.content[0].text == "A valid text block"


def test_text_block_non_string_text():
    """
    If a text block has a non-string `text`, raise ValueError.
    """
    message_param = {"content": [{"type": "text", "text": 123}]}
    with pytest.raises(
        ValueError, match="TextBlockParam must have a string 'text' field."
    ):
        AnthropicMessageParamConverter.from_provider([message_param])


def test_text_block_valid():
    """
    A valid text block should produce a single `BaseMessageParam` with `TextPart`.
    """
    message_param = {"content": [{"type": "text", "text": "Hello text"}]}
    results = AnthropicMessageParamConverter.from_provider([message_param])
    assert len(results) == 1

    result = results[0]
    assert len(result.content) == 1
    assert isinstance(result.content[0], TextPart)
    assert result.content[0].text == "Hello text"
    assert result.role == "assistant"


def test_image_block_no_source():
    """
    If image type is present but no `source`, raise ValueError.
    """
    message_param = {"content": [{"type": "image"}]}
    with pytest.raises(
        ValueError, match="ImageBlockParam must have a 'source' with type='base64'."
    ):
        AnthropicMessageParamConverter.from_provider([message_param])


def test_image_block_source_not_base64():
    """
    If an image block's source does not have type='base64', raise ValueError.
    """
    message_param = {"content": [{"type": "image", "source": {"type": "file"}}]}
    with pytest.raises(
        ValueError, match="ImageBlockParam must have a 'source' with type='base64'."
    ):
        AnthropicMessageParamConverter.from_provider([message_param])


def test_image_block_missing_data_or_media_type():
    """
    If an image block is missing `data` or `media_type`, raise ValueError.
    """
    message_param = {"content": [{"type": "image", "source": {"type": "base64"}}]}
    with pytest.raises(
        ValueError, match="ImageBlockParam source must have 'data' and 'media_type'."
    ):
        AnthropicMessageParamConverter.from_provider([message_param])


def test_image_block_unsupported_media_type():
    """
    If an image block's media_type is not recognized, raise ValueError.
    """
    message_param = {
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "data": base64.b64encode(b"fake").decode("utf-8"),
                    "media_type": "application/octet-stream",
                },
            }
        ]
    }
    with pytest.raises(
        ValueError, match="Unsupported image media type: application/octet-stream."
    ):
        AnthropicMessageParamConverter.from_provider([message_param])


def test_image_block_base64_str():
    """
    If the image source data is a base64-encoded string, decode it into image bytes.
    """
    img_data = b"fakeimage"
    b64_data = base64.b64encode(img_data).decode("utf-8")
    message_param = {
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "data": b64_data,
                    "media_type": "image/png",
                },
            }
        ]
    }
    results = AnthropicMessageParamConverter.from_provider([message_param])
    assert len(results) == 1

    result = results[0]
    assert isinstance(result.content[0], ImagePart)
    assert result.content[0].media_type == "image/png"
    assert result.content[0].image == img_data


def test_image_block_pathlike():
    """
    If the image source data is a PathLike object, open the file and read the data.
    """
    mock_file_data = b"pathlike image data"
    with patch("builtins.open", mock_open(read_data=mock_file_data)):

        class MockPath(PathLike):
            def __fspath__(self):
                return "fakepath.jpg"

        message_param = {
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "data": MockPath(),
                        "media_type": "image/jpeg",
                    },
                }
            ]
        }
        results = AnthropicMessageParamConverter.from_provider([message_param])
        assert len(results) == 1

        result = results[0]
        assert isinstance(result.content[0], ImagePart)
        assert result.content[0].media_type == "image/jpeg"
        assert result.content[0].image == mock_file_data


def test_image_block_filelike():
    """
    If the image source data is a file-like object, read() its data as bytes.
    """
    filelike_data = b"filelike image data"
    filelike = BytesIO(filelike_data)
    message_param = {
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "data": filelike,
                    "media_type": "image/gif",
                },
            }
        ]
    }
    results = AnthropicMessageParamConverter.from_provider([message_param])
    assert len(results) == 1

    result = results[0]
    assert isinstance(result.content[0], ImagePart)
    assert result.content[0].media_type == "image/gif"
    assert result.content[0].image == filelike_data


def test_tool_use_block():
    """
    A block with type="tool_use" should produce role="tool" and a `ToolCallPart`.
    """
    message_param = {
        "content": [
            {
                "type": "tool_use",
                "input": {"param": "value"},
                "id": "tool_id",
                "name": "tool_name",
            }
        ]
    }
    results = AnthropicMessageParamConverter.from_provider([message_param])
    assert len(results) == 1

    result = results[0]
    assert result.role == "tool"
    assert len(result.content) == 1
    assert isinstance(result.content[0], ToolCallPart)
    assert result.content[0].name == "tool_name"
    assert result.content[0].args == {"param": "value"}
    assert result.content[0].id == "tool_id"


def test_unsupported_block_type():
    """
    If a block has an unrecognized "type", raise ValueError.
    """
    message_param = {"content": [{"type": "unsupported"}]}
    with pytest.raises(ValueError, match="Unsupported block type 'unsupported'."):
        AnthropicMessageParamConverter.from_provider([message_param])


def test_mixed_content_tool_calls():
    """
    If content has both text blocks and tool_use blocks, the final role should be "tool".
    """
    message_param = {
        "content": [
            {"type": "text", "text": "Hello"},
            {
                "type": "tool_use",
                "input": {"arg": 123},
                "id": "tool_123",
                "name": "my_tool",
            },
        ]
    }
    results = AnthropicMessageParamConverter.from_provider([message_param])
    assert len(results) == 1

    result = results[0]
    assert result.role == "tool"
    assert len(result.content) == 2
    assert isinstance(result.content[0], TextPart)
    assert isinstance(result.content[1], ToolCallPart)


def test_empty_content_list():
    """
    If content is an empty list, default to role="assistant" with empty content.
    """
    message_param = {"content": []}
    results = AnthropicMessageParamConverter.from_provider([message_param])
    assert len(results) == 1

    result = results[0]
    assert result.role == "assistant"
    assert result.content == []
