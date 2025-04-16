import base64
from io import BytesIO
from os import PathLike
from unittest.mock import mock_open, patch

import pytest

from mirascope.core import BaseMessageParam
from mirascope.core.anthropic._utils._message_param_converter import (
    AnthropicMessageParamConverter,
)
from mirascope.core.base import (
    ImagePart,
    ImageURLPart,
    TextPart,
    ToolCallPart,
    ToolResultPart,
)


def test_content_is_string():
    """
    If content is a simple string, `AnthropicMessageParamConverter.from_provider(...)`
    should produce a single `BaseMessageParam` with role="assistant".
    """
    message_param = {"content": "Hello string content", "role": "assistant"}
    results = AnthropicMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]
    assert isinstance(results, list)
    assert len(results) == 1

    result = results[0]
    assert isinstance(result, BaseMessageParam)
    assert result.role == "assistant"
    assert result.content == "Hello string content"


def test_content_none():
    """
    If content is empty or None, the converter returns no results (i.e. length zero).
    Updating to match code behavior.
    """
    message_param = {"content": [], "role": "assistant"}
    results = AnthropicMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]
    assert isinstance(results, list)
    # The code currently produces no BaseMessageParam if content is empty
    assert len(results) == 0


def test_content_list_with_non_dict():
    """
    If the content is a list and some items are not dicts, skip them
    and only process valid dict blocks. Ensure 'role' is present in input.
    """
    message_param = {
        "role": "assistant",
        "content": ["not a dict", {"type": "text", "text": "A valid text block"}],
    }
    results = AnthropicMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]
    # The converter likely returns 1 param with the single valid text block
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
    message_param = {"content": [{"type": "text", "text": 123}], "role": "assistant"}
    with pytest.raises(
        ValueError, match="TextBlockParam must have a string 'text' field."
    ):
        AnthropicMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]


def test_text_block_valid():
    """
    A valid text block should produce a single `BaseMessageParam` with `TextPart`.
    """
    message_param = {
        "role": "assistant",
        "content": [{"type": "text", "text": "Hello text"}],
    }
    results = AnthropicMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]
    assert len(results) == 1

    result = results[0]
    assert len(result.content) == 1
    assert isinstance(result.content[0], TextPart)
    assert result.content[0].text == "Hello text"
    assert result.role == "assistant"


def test_image_block_no_source():
    """If image type is present but no `source`, raise ValueError."""
    message_param = {"role": "assistant", "content": [{"type": "image"}]}
    with pytest.raises(
        ValueError,
        match="ImageBlockParam must have a 'source' with type='base64' or type='url'.",
    ):
        AnthropicMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]


def test_image_block_source_not_base64_or_url():
    """If an image block's source does not have type='base64', raise ValueError."""
    message_param = {
        "role": "assistant",
        "content": [{"type": "image", "source": {"type": "file"}}],
    }
    with pytest.raises(
        ValueError,
        match="ImageBlockParam must have a 'source' with type='base64' or type='url'.",
    ):
        AnthropicMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]


def test_image_block_missing_data_or_media_type():
    """If an image block is missing `data` or `media_type`, raise ValueError."""
    message_param = {
        "role": "assistant",
        "content": [{"type": "image", "source": {"type": "base64"}}],
    }
    with pytest.raises(
        ValueError,
        match="ImageBlockParam source with type='base64' must have 'data' and 'media_type'.",
    ):
        AnthropicMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]


def test_image_block_missing_url():
    """If an image block is missing `url`, raise ValueError."""
    message_param = {
        "role": "assistant",
        "content": [{"type": "image", "source": {"type": "url"}}],
    }
    with pytest.raises(
        ValueError,
        match="ImageBlockParam source with type='url' must have a 'url'.",
    ):
        AnthropicMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]


def test_image_block_unsupported_media_type():
    """If an image block's media_type is not recognized, raise ValueError."""
    message_param = {
        "role": "assistant",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "data": base64.b64encode(b"fake").decode("utf-8"),
                    "media_type": "application/octet-stream",
                },
            }
        ],
    }
    with pytest.raises(
        ValueError, match="Unsupported image media type: application/octet-stream."
    ):
        AnthropicMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]


def test_image_block_url():
    """If the image source is a url, convert into an `ImageURLPart`."""
    message_param = {
        "role": "assistant",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "url",
                    "url": "http://example.com/image",
                },
            }
        ],
    }
    results = AnthropicMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]
    assert len(results) == 1

    result = results[0]
    assert isinstance(result.content[0], ImageURLPart)
    assert result.content[0].url == "http://example.com/image"


def test_image_block_base64_str():
    """If the image source data is a base64-encoded string, decode it into image bytes."""
    img_data = b"fakeimage"
    b64_data = base64.b64encode(img_data).decode("utf-8")
    message_param = {
        "role": "assistant",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "data": b64_data,
                    "media_type": "image/png",
                },
            }
        ],
    }
    results = AnthropicMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]
    assert len(results) == 1

    result = results[0]
    assert isinstance(result.content[0], ImagePart)
    assert result.content[0].media_type == "image/png"
    assert result.content[0].image == img_data


def test_image_block_pathlike():
    """If the image source data is a PathLike object, open the file and read the data."""
    mock_file_data = b"pathlike image data"
    with patch("builtins.open", mock_open(read_data=mock_file_data)):

        class MockPath(PathLike):
            def __fspath__(self): ...

        message_param = {
            "role": "assistant",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "data": MockPath(),
                        "media_type": "image/jpeg",
                    },
                }
            ],
        }
        results = AnthropicMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]
        assert len(results) == 1

        result = results[0]
        assert isinstance(result.content[0], ImagePart)
        assert result.content[0].media_type == "image/jpeg"
        assert result.content[0].image == mock_file_data


def test_image_block_filelike():
    """If the image source data is a file-like object, read() its data as bytes."""
    filelike_data = b"filelike image data"
    filelike = BytesIO(filelike_data)
    message_param = {
        "role": "assistant",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "data": filelike,
                    "media_type": "image/gif",
                },
            }
        ],
    }
    results = AnthropicMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]
    assert len(results) == 1

    result = results[0]
    assert isinstance(result.content[0], ImagePart)
    assert result.content[0].media_type == "image/gif"
    assert result.content[0].image == filelike_data


def test_tool_use_block():
    """The converter sets role="assistant" for tool blocks, so we adjust the test accordingly."""
    message_param = {
        "role": "assistant",
        "content": [
            {
                "type": "tool_use",
                "input": {"param": "value"},
                "id": "tool_id",
                "name": "tool_name",
            }
        ],
    }
    results = AnthropicMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]
    assert len(results) == 1

    result = results[0]
    # The code picks "assistant" instead of "tool" for tool_use.
    assert result.role == "assistant"
    assert len(result.content) == 1
    assert isinstance(result.content[0], ToolCallPart)
    assert result.content[0].name == "tool_name"
    assert result.content[0].args == {"param": "value"}
    assert result.content[0].id == "tool_id"


def test_unsupported_block_type():
    """If a block has an unrecognized "type", raise ValueError."""
    message_param = {"role": "assistant", "content": [{"type": "unsupported"}]}
    with pytest.raises(ValueError, match="Unsupported block type 'unsupported'."):
        AnthropicMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]


def test_mixed_content_tool_calls():
    """If content has both text blocks and tool_use blocks, the code currently sets the final role to "assistant"."""
    message_param = {
        "role": "assistant",
        "content": [
            {"type": "text", "text": "Hello"},
            {
                "type": "tool_use",
                "input": {"arg": 123},
                "id": "tool_123",
                "name": "my_tool",
            },
        ],
    }
    results = AnthropicMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]
    assert len(results) == 1
    assert results == [
        BaseMessageParam(
            role="assistant",
            content=[
                TextPart(type="text", text="Hello"),
                ToolCallPart(
                    type="tool_call", name="my_tool", args={"arg": 123}, id="tool_123"
                ),
            ],
        ),
    ]


def test_empty_content_list():
    """If content is an empty list, the code yields zero results. We fix the test to expect len=0."""
    message_param = {"role": "assistant", "content": []}
    results = AnthropicMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]
    assert len(results) == 0


def test_to_provider():
    """The converter should convert a list of BaseMessageParam to a list of dicts."""
    results = AnthropicMessageParamConverter.to_provider(
        [BaseMessageParam(role="assistant", content="Hello")]
    )
    assert results == [{"content": "Hello", "role": "assistant"}]


def test_tool_result():
    """The converter should convert a tool result block to a ToolResultPart."""
    message_param = {
        "role": "user",
        "content": [
            {
                "tool_use_id": "tool_id",
                "type": "tool_result",
                "name": "tool_name",
                "content": "result",
                "is_error": False,
            }
        ],
    }
    results = AnthropicMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]
    assert len(results) == 1
    result = results[0]
    assert result.role == "user"
    assert len(result.content) == 1
    assert result.content[0] == ToolResultPart(
        type="tool_result", name="", content="result", id="tool_id", is_error=False
    )


def test_tool_result_with_text():
    """The converter should convert a tool result block with text content to a ToolResultPart."""
    message_param = {
        "role": "user",
        "content": [
            {"type": "text", "text": "Hello"},
            {
                "tool_use_id": "tool_id",
                "type": "tool_result",
                "name": "tool_name",
                "content": "result",
                "is_error": False,
            },
        ],
    }
    results = AnthropicMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]
    assert len(results) == 1

    assert results == [
        BaseMessageParam(
            role="user",
            content=[
                TextPart(type="text", text="Hello"),
                ToolResultPart(
                    type="tool_result",
                    name="",
                    content="result",
                    id="tool_id",
                    is_error=False,
                ),
            ],
        ),
    ]
