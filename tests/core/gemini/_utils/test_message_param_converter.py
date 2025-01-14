# test_gemini_message_param_converter.py
from unittest.mock import MagicMock

import pytest

from mirascope.core import BaseMessageParam
from mirascope.core.base import DocumentPart, ImagePart, TextPart, ToolCallPart
from mirascope.core.gemini._utils._message_param_converter import (
    GeminiMessageParamConverter,
)


def test_gemini_convert_parts_text_only():
    """
    If parts contain only text, produce one TextPart if multiple or a single string if just one.
    """
    mock_part = MagicMock()
    mock_part.text = "hello world"
    mock_part.inline_data = None
    mock_part.file_data = None
    mock_part.function_call = None

    results = GeminiMessageParamConverter.from_provider(
        [{"role": "assistant", "parts": [mock_part]}]
    )
    assert len(results) == 1

    result = results[0]
    assert isinstance(result, BaseMessageParam)
    assert result.role == "assistant"
    # one text part -> might become a single string
    # multiple text parts -> a list of TextPart
    # depends on your converter logic
    if isinstance(result.content, list):
        assert len(result.content) == 1
        assert isinstance(result.content[0], TextPart)
        assert result.content[0].text == "hello world"
    else:
        # single string
        assert result.content == "hello world"


def test_gemini_convert_parts_image():
    InlineData = MagicMock()
    mock_part = MagicMock()
    mock_part.text = None
    mock_part.file_data = None
    mock_part.function_call = None

    mock_inline_data = InlineData()
    mock_inline_data.mime_type = "image/png"
    mock_inline_data.data = b"\x89PNG\r\n\x1a\n"
    mock_part.inline_data = mock_inline_data

    results = GeminiMessageParamConverter.from_provider(
        [{"role": "assistant", "parts": [mock_part]}]
    )
    result = results[0]
    assert len(result.content) == 1
    assert isinstance(result.content[0], ImagePart)
    assert result.content[0].media_type == "image/png"


def test_gemini_convert_parts_document():
    FileData = MagicMock()
    mock_part = MagicMock()
    mock_part.text = None
    mock_part.inline_data = None
    mock_part.function_call = None

    mock_file_data = FileData()
    mock_file_data.mime_type = "application/pdf"
    mock_file_data.data = b"%PDF-1.4..."
    mock_part.file_data = mock_file_data

    results = GeminiMessageParamConverter.from_provider(
        [{"role": "assistant", "parts": [mock_part]}]
    )
    result = results[0]
    assert len(result.content) == 1
    doc_part = result.content[0]
    assert isinstance(doc_part, DocumentPart)
    assert doc_part.media_type == "application/pdf"


def test_gemini_convert_parts_unsupported_image():
    mock_part = MagicMock()
    mock_part.text = None
    mock_part.file_data = None
    mock_part.function_call = None

    mock_inline_data = MagicMock()
    mock_inline_data.mime_type = "image/tiff"
    mock_inline_data.data = b"fake"
    mock_part.inline_data = mock_inline_data

    with pytest.raises(
        ValueError,
        match="Unsupported inline_data mime type: image/tiff. Cannot convert to BaseMessageParam.",
    ):
        GeminiMessageParamConverter.from_provider(
            [{"role": "assistant", "parts": [mock_part]}]
        )


def test_gemini_convert_parts_unsupported_document():
    mock_part = MagicMock()
    mock_part.text = None
    mock_part.inline_data = None
    mock_part.function_call = None

    mock_file_data = MagicMock()
    mock_file_data.mime_type = "application/msword"
    mock_file_data.data = b"DOC..."
    mock_part.file_data = mock_file_data

    with pytest.raises(
        ValueError,
        match="Unsupported file_data mime type: application/msword. Cannot convert to BaseMessageParam.",
    ):
        GeminiMessageParamConverter.from_provider(
            [{"role": "assistant", "parts": [mock_part]}]
        )


def test_gemini_convert_function_call():
    mock_part = MagicMock()
    mock_part.text = None
    mock_part.inline_data = None
    mock_part.file_data = None

    function_call = MagicMock()
    function_call.name = "some_tool"
    function_call.args = {"param1": "value1"}
    mock_part.function_call = function_call

    results = GeminiMessageParamConverter.from_provider(
        [{"role": "assistant", "parts": [mock_part]}]
    )
    result = results[0]
    assert isinstance(result, BaseMessageParam)
    assert len(result.content) == 1
    part = result.content[0]
    assert isinstance(part, ToolCallPart)
    assert part.name == "some_tool"


def test_gemini_convert_no_supported_content():
    mock_part = MagicMock()
    mock_part.text = None
    mock_part.inline_data = None
    mock_part.file_data = None
    mock_part.function_call = None

    with pytest.raises(
        ValueError,
        match="Part does not contain any supported content \\(text, image, or document\\).",
    ):
        GeminiMessageParamConverter.from_provider(
            [{"role": "assistant", "parts": [mock_part]}]
        )
