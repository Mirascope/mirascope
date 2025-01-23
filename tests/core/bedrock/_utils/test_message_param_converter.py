import pytest

from mirascope.core import BaseMessageParam
from mirascope.core.base import (
    DocumentPart,
    ImagePart,
    TextPart,
    ToolCallPart,
    ToolResultPart,
)
from mirascope.core.bedrock._utils._message_param_converter import (
    BedrockMessageParamConverter,
)


def test_single_text():
    message_param = {"role": "assistant", "content": [{"text": "Hello world"}]}
    results = BedrockMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]
    assert len(results) == 1

    result = results[0]
    assert isinstance(result, BaseMessageParam)
    assert result.role == "assistant"
    assert result.content == "Hello world"


def test_multiple_text():
    message_param = {
        "role": "assistant",
        "content": [{"text": "Hello"}, {"text": "World"}],
    }
    results = BedrockMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]
    assert len(results) == 1

    result = results[0]
    assert isinstance(result.content, list)
    assert len(result.content) == 2
    assert isinstance(result.content[0], TextPart)
    assert result.content[0].text == "Hello"
    assert isinstance(result.content[1], TextPart)
    assert result.content[1].text == "World"


def test_text_not_string():
    message_param = {"role": "assistant", "content": [{"text": 123}]}
    with pytest.raises(ValueError, match="Text content must be a string."):
        BedrockMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]


def test_image_block_valid():
    message_param = {
        "role": "assistant",
        "content": [
            {"image": {"format": "JPEG", "source": {"bytes": b"fake_jpeg_data"}}}
        ],
    }
    results = BedrockMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]
    result = results[0]
    assert len(result.content) == 1
    img_part = result.content[0]
    assert isinstance(img_part, ImagePart)
    assert img_part.media_type == "image/jpeg"
    assert img_part.image == b"fake_jpeg_data"


def test_image_block_missing_bytes():
    message_param = {
        "role": "assistant",
        "content": [{"image": {"format": "PNG", "source": {}}}],
    }
    with pytest.raises(
        ValueError, match="Image block must have 'source.bytes' as bytes."
    ):
        BedrockMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]


def test_image_block_unsupported_format():
    message_param = {
        "role": "assistant",
        "content": [{"image": {"format": "TIFF", "source": {"bytes": b"something"}}}],
    }
    with pytest.raises(ValueError, match="Unsupported image format: TIFF"):
        BedrockMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]


def test_document_block_valid():
    message_param = {
        "role": "assistant",
        "content": [{"document": {"format": "PDF", "source": {"bytes": b"pdf_data"}}}],
    }
    results = BedrockMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]
    result = results[0]
    assert len(result.content) == 1
    doc_part = result.content[0]
    assert isinstance(doc_part, DocumentPart)
    assert doc_part.media_type == "application/pdf"
    assert doc_part.document == b"pdf_data"


def test_document_block_unsupported_format():
    message_param = {
        "role": "assistant",
        "content": [{"document": {"format": "DOCX", "source": {"bytes": b"doc_data"}}}],
    }
    with pytest.raises(ValueError, match="Unsupported document format: DOCX"):
        BedrockMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]


def test_document_block_missing_bytes():
    message_param = {
        "role": "assistant",
        "content": [{"document": {"format": "PDF", "source": {}}}],
    }
    with pytest.raises(
        ValueError, match="Document block must have 'source.bytes' as bytes."
    ):
        BedrockMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]


def test_tool_use_block():
    message_param = {
        "role": "assistant",
        "content": [
            {
                "toolUse": {
                    "name": "my_tool",
                    "toolUseId": "tool_123",
                    "input": {"arg": "val"},
                }
            }
        ],
    }
    results = BedrockMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]
    result = results[0]
    assert result.role == "assistant"
    assert len(result.content) == 1
    part = result.content[0]
    assert isinstance(part, ToolCallPart)
    assert part.name == "my_tool"
    assert part.id == "tool_123"
    assert part.args == {"arg": "val"}


def test_no_supported_content():
    message_param = {"role": "assistant", "content": [{}]}
    with pytest.raises(
        ValueError, match="Content block does not contain supported content."
    ):
        BedrockMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]


def test_empty_content():
    message_param = {"role": "assistant", "content": []}
    results = BedrockMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]
    assert not results


def test_tool_result():
    message_param = {
        "role": "user",
        "content": [
            {
                "toolResult": {
                    "toolUseId": "tool_123",
                    "content": [{"text": "result"}],
                    "name": "tool_123",
                }
            }
        ],
    }
    results = BedrockMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]
    assert results == [
        BaseMessageParam(
            role="user",
            content=[
                ToolResultPart(
                    type="tool_result",
                    name="tool_123",
                    content="result",
                    id="tool_123",
                    is_error=False,
                )
            ],
        )
    ]


def test_tool_use_with_text():
    message_param = {
        "role": "user",
        "content": [
            {"text": "Hello"},
            {
                "toolUse": {
                    "name": "tool_name",
                    "toolUseId": "tool_id",
                    "input": {"arg": "val"},
                }
            },
        ],
    }
    results = BedrockMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]
    assert results == [
        BaseMessageParam(role="user", content=[TextPart(type="text", text="Hello")]),
        BaseMessageParam(
            role="assistant",
            content=[
                ToolCallPart(
                    type="tool_call",
                    name="tool_name",
                    args={"arg": "val"},
                    id="tool_id",
                )
            ],
        ),
    ]


def test_tool_result_with_text():
    message_param = {
        "role": "user",
        "content": [
            {"text": "Hello"},
            {
                "toolResult": {
                    "toolUseId": "tool_id",
                    "content": [{"text": "result"}],
                    "name": "tool_name",
                }
            },
        ],
    }
    results = BedrockMessageParamConverter.from_provider([message_param])  # pyright: ignore [reportArgumentType]
    assert results == [
        BaseMessageParam(role="user", content=[TextPart(type="text", text="Hello")]),
        BaseMessageParam(
            role="user",
            content=[
                ToolResultPart(
                    type="tool_result",
                    name="tool_name",
                    content="result",
                    id="tool_id",
                    is_error=False,
                )
            ],
        ),
    ]


def test_to_provider():
    message_param = BaseMessageParam(
        role="assistant",
        content=[
            TextPart(type="text", text="Hello, world!"),
            ToolCallPart(type="tool_call", name="test_tool", args={"key": "value"}),
        ],
    )
    results = BedrockMessageParamConverter.to_provider([message_param])
    assert results == [
        {"content": [{"text": "Hello, world!"}], "role": "assistant"},
        {
            "content": [
                {
                    "toolUse": {
                        "input": {"key": "value"},
                        "name": "test_tool",
                        "toolUseId": None,
                    }
                }
            ],
            "role": "assistant",
        },
    ]
