# file: tests/core/gemini/_utils/test_message_param_converter.py

import pytest
from google.generativeai import protos

from mirascope.core import BaseMessageParam
from mirascope.core.base import DocumentPart, ImagePart, TextPart, ToolCallPart
from mirascope.core.gemini._utils._message_param_converter import (
    GeminiMessageParamConverter,
)


def test_gemini_convert_parts_text_only():
    """
    If parts contain only text, the converter should produce
    a BaseMessageParam with either a single text string or a list[TextPart].
    """
    part = protos.Part(text="hello world")
    results = GeminiMessageParamConverter.from_provider(
        [
            {
                "role": "assistant",
                "parts": [part],
            }
        ]
    )
    assert len(results) == 1
    result = results[0]
    assert isinstance(result, BaseMessageParam)
    assert result.role == "assistant"

    # If the converter merges a single text into a plain string:
    if isinstance(result.content, str):
        assert result.content == "hello world"
    else:
        # Otherwise, if it keeps them as TextPart objects:
        assert len(result.content) == 1
        assert isinstance(result.content[0], TextPart)
        assert result.content[0].text == "hello world"


def test_gemini_convert_parts_image():
    """
    If inline_data has an image mime type, produce an ImagePart.
    """
    part = protos.Part(
        inline_data=protos.Blob(mime_type="image/png", data=b"\x89PNG\r\n\x1a\n")
    )
    results = GeminiMessageParamConverter.from_provider(
        [{"role": "assistant", "parts": [part]}]
    )
    assert len(results) == 1
    result = results[0]
    assert isinstance(result.content, list)
    assert len(result.content) == 1
    assert isinstance(result.content[0], ImagePart)
    assert result.content[0].media_type == "image/png"
    assert result.content[0].image == b"\x89PNG\r\n\x1a\n"


def test_gemini_convert_parts_document():
    """
    If file_data is a PDF, produce a DocumentPart.
    """
    part = protos.Part(
        file_data=protos.FileData(mime_type="application/pdf", file_uri=b"%PDF-1.4...")
    )
    results = GeminiMessageParamConverter.from_provider(
        [{"role": "assistant", "parts": [part]}]
    )
    assert len(results) == 1
    result = results[0]
    assert isinstance(result.content, list)
    assert len(result.content) == 1
    doc_part = result.content[0]
    assert isinstance(doc_part, DocumentPart)
    assert doc_part.media_type == "application/pdf"
    assert doc_part.document == b"%PDF-1.4..."


def test_gemini_convert_parts_unsupported_image():
    """
    If inline_data has an unsupported image type (e.g. image/tiff),
    the converter should raise ValueError.
    """
    part = protos.Part(inline_data=protos.Blob(mime_type="image/tiff", data=b"fake"))
    with pytest.raises(
        ValueError,
        match="Unsupported inline_data mime type: image/tiff. Cannot convert to BaseMessageParam.",
    ):
        GeminiMessageParamConverter.from_provider(
            [{"role": "assistant", "parts": [part]}]
        )


def test_gemini_convert_parts_unsupported_document():
    """
    If file_data has a non-PDF type (e.g. application/msword),
    the converter should raise ValueError.
    """
    part = protos.Part(
        file_data=protos.FileData(mime_type="application/msword", file_uri=b"DOC...")
    )
    with pytest.raises(
        ValueError,
        match="Unsupported file_data mime type: application/msword. Cannot convert to BaseMessageParam.",
    ):
        GeminiMessageParamConverter.from_provider(
            [{"role": "assistant", "parts": [part]}]
        )


def test_gemini_convert_function_call():
    """
    If the part has a function_call, the converter returns a new BaseMessageParam
    with a ToolCallPart inside.
    """
    part = protos.Part(
        function_call=protos.FunctionCall(name="some_tool", args={"param1": "value1"})
    )
    results = GeminiMessageParamConverter.from_provider(
        [{"role": "assistant", "parts": [part]}]
    )
    assert len(results) == 1
    result = results[0]
    assert isinstance(result.content, list)
    assert len(result.content) == 1
    part_call = result.content[0]
    assert isinstance(part_call, ToolCallPart)
    assert part_call.name == "some_tool"
    assert part_call.args == {"param1": "value1"}


def test_gemini_convert_no_supported_content():
    """
    If none of text, inline_data, file_data, function_call, or function_response
    is set, the converter should raise ValueError.
    """
    part = protos.Part()
    # No text, no inline_data, no file_data, no function_call, no function_response
    with pytest.raises(
        ValueError,
        match="Part does not contain any supported content \\(text, image, or document\\).",
    ):
        GeminiMessageParamConverter.from_provider(
            [{"role": "assistant", "parts": [part]}]
        )
