from unittest.mock import MagicMock

import pytest

from mirascope.core import BaseMessageParam
from mirascope.core.base import DocumentPart, ImagePart, TextPart
from mirascope.core.gemini._utils._convert_message_param_to_base_message_param import (
    _to_document_part,
    _to_image_part,
    convert_message_param_to_base_message_param,
)


def test_gemini_convert_parts_text_only():
    """
    Test gemini_convert_parts with a Part containing only text.
    """
    Part = MagicMock()  # Mock Part class
    mock_part = Part()
    mock_part.text = "hello world"
    mock_part.inline_data = None
    mock_part.file_data = None

    result = convert_message_param_to_base_message_param(
        {"role": "assistant", "parts": [mock_part]}
    )
    assert isinstance(result, BaseMessageParam)
    assert result.role == "assistant"
    assert len(result.content) == 1
    assert isinstance(result.content[0], TextPart)
    assert result.content[0].text == "hello world"


def test_gemini_convert_parts_image():
    """
    Test gemini_convert_parts with an image inline_data.
    """
    Part = MagicMock()
    InlineData = MagicMock()
    mock_part = Part()
    mock_part.text = None
    mock_part.file_data = None

    mock_inline_data = InlineData()
    mock_inline_data.mime_type = "image/png"
    mock_inline_data.data = b"\x89PNG\r\n\x1a\n"
    mock_part.inline_data = mock_inline_data

    result = convert_message_param_to_base_message_param(
        {"role": "assistant", "parts": [mock_part]}
    )
    assert isinstance(result, BaseMessageParam)
    assert len(result.content) == 1
    assert isinstance(result.content[0], ImagePart)
    assert result.content[0].media_type == "image/png"


def test_gemini_convert_parts_document():
    """
    Test gemini_convert_parts with a PDF document file_data.
    """
    Part = MagicMock()
    FileData = MagicMock()
    mock_part = Part()
    mock_part.text = None
    mock_part.inline_data = None

    mock_file_data = FileData()
    mock_file_data.mime_type = "application/pdf"
    mock_file_data.data = b"%PDF-1.4..."
    mock_part.file_data = mock_file_data

    result = convert_message_param_to_base_message_param(
        {"role": "assistant", "parts": [mock_part]}
    )
    assert isinstance(result, BaseMessageParam)
    assert len(result.content) == 1
    assert isinstance(result.content[0], DocumentPart)
    assert result.content[0].media_type == "application/pdf"


def test_gemini_convert_parts_unsupported_image():
    """
    Test gemini_convert_parts with unsupported image mime type.
    """
    Part = MagicMock()
    InlineData = MagicMock()
    mock_part = Part()
    mock_part.text = None
    mock_part.file_data = None
    mock_inline_data = InlineData()
    mock_inline_data.mime_type = "image/tiff"  # not supported
    mock_inline_data.data = b"fake"
    mock_part.inline_data = mock_inline_data

    with pytest.raises(
        ValueError,
        match="Unsupported inline_data mime type: image/tiff. Cannot convert to BaseMessageParam.",
    ):
        convert_message_param_to_base_message_param(
            {"role": "assistant", "parts": [mock_part]}
        )


def test_gemini_convert_parts_unsupported_document():
    """
    Test gemini_convert_parts with an unsupported document mime type.
    """
    Part = MagicMock()
    FileData = MagicMock()
    mock_part = Part()
    mock_part.text = None
    mock_part.inline_data = None
    mock_file_data = FileData()
    mock_file_data.mime_type = "application/msword"  # not supported
    mock_file_data.data = b"DOC..."
    mock_part.file_data = mock_file_data

    with pytest.raises(
        ValueError,
        match="Unsupported file_data mime type: application/msword. Cannot convert to BaseMessageParam.",
    ):
        convert_message_param_to_base_message_param(
            {"role": "assistant", "parts": [mock_part]}
        )


def test_gemini_convert_parts_file_data_image():
    """
    Test convert_message_param_to_base_message_param with file_data as image.
    Covers the line in file_data section:
    if _is_image_mime(mime):
        contents.append(_to_image_part(mime, data))
    """
    Part = MagicMock()
    FileData = MagicMock()
    mock_part = Part()
    mock_part.text = None
    mock_part.inline_data = None

    mock_file_data = FileData()
    mock_file_data.mime_type = "image/jpeg"
    mock_file_data.data = b"fake_jpeg_data"
    mock_part.file_data = mock_file_data

    result = convert_message_param_to_base_message_param(
        {"role": "assistant", "parts": [mock_part]}
    )
    assert isinstance(result, BaseMessageParam)
    assert len(result.content) == 1
    assert isinstance(result.content[0], ImagePart)
    assert result.content[0].media_type == "image/jpeg"


def test_gemini_convert_parts_inline_data_pdf():
    """
    Test convert_message_param_to_base_message_param with inline_data as PDF.
    Covers the line in inline_data section:
    elif mime == "application/pdf":
        contents.append(_to_document_part(mime, data))
    """
    Part = MagicMock()
    InlineData = MagicMock()
    mock_part = Part()
    mock_part.text = None
    mock_part.file_data = None

    mock_inline_data = InlineData()
    mock_inline_data.mime_type = "application/pdf"
    mock_inline_data.data = b"%PDF-1.4..."
    mock_part.inline_data = mock_inline_data

    result = convert_message_param_to_base_message_param(
        {"role": "assistant", "parts": [mock_part]}
    )
    assert isinstance(result, BaseMessageParam)
    assert len(result.content) == 1
    assert isinstance(result.content[0], DocumentPart)
    assert result.content[0].media_type == "application/pdf"


def test_gemini_convert_function_call():
    """
    Test that convert_message_param_to_base_message_param returns immediately with a function_call.
    Covers the line:
    elif part.function_call:
        return BaseMessageParam(...)
    """
    Part = MagicMock()
    FunctionCall = MagicMock()
    mock_part = Part()
    mock_part.text = None
    mock_part.inline_data = None
    mock_part.file_data = None
    mock_function_call = FunctionCall()
    mock_function_call.name = "some_tool"
    mock_function_call.args = {"param1": "value1"}
    mock_part.function_call = mock_function_call

    result = convert_message_param_to_base_message_param(
        {"role": "assistant", "parts": [mock_part]}
    )
    assert isinstance(result, BaseMessageParam)
    assert len(result.content) == 1
    assert result.content[0].type == "tool_call"
    assert result.content[0].name == "some_tool"


def test_gemini_convert_no_supported_content():
    """
    Test that convert_message_param_to_base_message_param raises ValueError if no supported content is present.
    Covers the line:
    else:
        raise ValueError("Part does not contain any supported content (text, image, or document).")
    """
    Part = MagicMock()
    mock_part = Part()
    mock_part.text = None
    mock_part.inline_data = None
    mock_part.file_data = None
    mock_part.function_call = None

    with pytest.raises(
        ValueError,
        match="Part does not contain any supported content \\(text, image, or document\\).",
    ):
        convert_message_param_to_base_message_param(
            {"role": "assistant", "parts": [mock_part]}
        )


def test_to_document_part_unsupported():
    """
    Test that _to_document_part raises ValueError with unsupported document mime type.
    Covers the line:
    if mime_type != "application/pdf":
        raise ValueError(...)
    """
    with pytest.raises(
        ValueError,
        match="Unsupported document media type: application/msword. Only application/pdf is supported.",
    ):
        _to_document_part("application/msword", b"fake_data")


def test_to_image_part_unsupported():
    """
    Test that _to_image_part raises ValueError with unsupported image mime type.
    Covers the line:
    if not _is_image_mime(mime_type):
        raise ValueError(...)
    """
    with pytest.raises(
        ValueError,
        match="Unsupported image media type: image/tiff. Expected one of: image/jpeg, image/png, image/gif, image/webp.",
    ):
        _to_image_part("image/tiff", b"fake_data")
