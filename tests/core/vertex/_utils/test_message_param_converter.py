from unittest.mock import MagicMock

import pytest

from mirascope.core import BaseMessageParam
from mirascope.core.base import DocumentPart, ImagePart, TextPart
from mirascope.core.vertex._utils._message_param_converter import (
    VertexMessageParamConverter,
)


def test_vertex_convert_parts_text_only():
    Part = MagicMock()
    mock_part = Part()
    mock_part.text = "hello world"
    mock_part.inline_data = None
    mock_part.file_data = None
    mock_part.function_call = None
    message = MagicMock()
    message.parts = [mock_part]
    results = VertexMessageParamConverter.from_provider([message])
    assert len(results) == 1

    result = results[0]
    assert isinstance(result, BaseMessageParam)
    assert len(result.content) == 1
    part = result.content[0]
    assert isinstance(part, TextPart)
    assert part.text == "hello world"


def test_vertex_convert_parts_image():
    Part = MagicMock()
    InlineData = MagicMock()
    mock_part = Part()
    mock_part.text = None
    mock_part.file_data = None
    mock_part.function_call = None

    mock_inline_data = InlineData()
    mock_inline_data.mime_type = "image/png"
    mock_inline_data.data = b"\x89PNG\r\n\x1a\n"
    mock_part.inline_data = mock_inline_data
    message = MagicMock()
    message.parts = [mock_part]
    results = VertexMessageParamConverter.from_provider([message])
    result = results[0]
    assert isinstance(result, BaseMessageParam)
    assert len(result.content) == 1
    img_part = result.content[0]
    assert isinstance(img_part, ImagePart)
    assert img_part.media_type == "image/png"


def test_vertex_convert_parts_document():
    Part = MagicMock()
    FileData = MagicMock()
    mock_part = Part()
    mock_part.text = None
    mock_part.inline_data = None
    mock_part.function_call = None

    mock_file_data = FileData()
    mock_file_data.mime_type = "application/pdf"
    mock_file_data.data = b"%PDF-1.4..."
    mock_part.file_data = mock_file_data
    message = MagicMock()
    message.parts = [mock_part]
    results = VertexMessageParamConverter.from_provider([message])
    result = results[0]
    assert len(result.content) == 1
    doc_part = result.content[0]
    assert isinstance(doc_part, DocumentPart)
    assert doc_part.media_type == "application/pdf"


def test_vertex_convert_parts_unsupported_image():
    Part = MagicMock()
    InlineData = MagicMock()
    mock_part = Part()
    mock_part.text = None
    mock_part.file_data = None
    mock_part.function_call = None

    mock_inline_data = InlineData()
    mock_inline_data.mime_type = "image/tiff"
    mock_inline_data.data = b"fake"
    mock_part.inline_data = mock_inline_data
    message = MagicMock()
    message.parts = [mock_part]
    with pytest.raises(
        ValueError,
        match="Unsupported inline_data mime type: image/tiff. Cannot convert to BaseMessageParam.",
    ):
        VertexMessageParamConverter.from_provider([message])


def test_vertex_convert_parts_unsupported_document():
    Part = MagicMock()
    FileData = MagicMock()
    mock_part = Part()
    mock_part.text = None
    mock_part.inline_data = None
    mock_part.function_call = None

    mock_file_data = FileData()
    mock_file_data.mime_type = "application/msword"
    mock_file_data.data = b"DOC..."
    mock_part.file_data = mock_file_data
    message = MagicMock()
    message.parts = [mock_part]
    with pytest.raises(
        ValueError,
        match="Unsupported file_data mime type: application/msword. Cannot convert to BaseMessageParam.",
    ):
        VertexMessageParamConverter.from_provider([message])


def test_vertex_convert_parts_tool_result():
    Part = MagicMock()
    mock_part = Part()
    mock_part.text = None
    mock_part.inline_data = None
    mock_part.file_data = None
    function_call = MagicMock()
    function_call.name = "test"
    function_call.arguments = [("arg1", "value1")]
    mock_part.function_call = function_call
    message = MagicMock()
    message.parts = [mock_part]
    results = VertexMessageParamConverter.from_provider([message])
    assert len(results) == 1

    result = results[0]
    assert result.role == "tool"
    assert len(result.content) == 1
    part = result.content[0]
    assert part.type == "tool_call"
    assert part.name == "test"


def test_vertex_convert_parts_no_supported_content():
    Part = MagicMock()
    mock_part = Part()
    mock_part.text = None
    mock_part.inline_data = None
    mock_part.file_data = None
    mock_part.function_call = None
    message = MagicMock()
    message.parts = [mock_part]
    with pytest.raises(
        ValueError,
        match="Part does not contain any supported content \\(text, image, or document\\).",
    ):
        VertexMessageParamConverter.from_provider([message])
