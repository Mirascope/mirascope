from unittest.mock import MagicMock

import pytest

from mirascope.core import BaseMessageParam
from mirascope.core.base import DocumentPart, ImagePart, TextPart
from mirascope.core.gemini._utils._convert_parts_to_base_message_param import (
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


def test_gemini_convert_parts_empty_part():
    """
    Test gemini_convert_parts with an empty part (no text, no inline_data, no file_data).
    """
    Part = MagicMock()
    mock_part = Part()
    mock_part.text = None
    mock_part.inline_data = None
    mock_part.file_data = None

    with pytest.raises(ValueError, match="Part does not contain any supported content"):
        convert_message_param_to_base_message_param(
            {"role": "assistant", "parts": [mock_part]}
        )
