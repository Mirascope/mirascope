import pytest
from google.generativeai import protos

from mirascope.core import BaseMessageParam
from mirascope.core.base import (
    AudioPart,
    AudioURLPart,
    DocumentPart,
    ImagePart,
    ImageURLPart,
)
from mirascope.core.base.message_param import ToolCallPart, ToolResultPart
from mirascope.core.gemini._utils._message_param_converter import (
    GeminiMessageParamConverter,
    _to_audio_part,
    _to_document_part,
    _to_image_part,
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

    assert result.content == "hello world"


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


def test_gemini_convert_parts_audio():
    part = protos.Part(inline_data=protos.Blob(mime_type="audio/mp3", data=b"audio"))
    results = GeminiMessageParamConverter.from_provider(
        [{"role": "assistant", "parts": [part]}]
    )
    assert len(results) == 1
    result = results[0]
    assert isinstance(result.content, list)
    assert len(result.content) == 1
    assert isinstance(result.content[0], AudioPart)
    assert result.content[0].media_type == "audio/mp3"
    assert result.content[0].audio == b"audio"


def test_gemini_convert_parts_document():
    """
    If file_data is a PDF, produce a DocumentPart.
    """
    part = protos.Part(
        file_data=protos.FileData(mime_type="application/pdf", file_uri=b"%PDF-1.4...")
    )
    with pytest.raises(
        ValueError,
        match="Unsupported file_data mime type: application/pdf. Cannot convert to BaseMessageParam.",
    ):
        GeminiMessageParamConverter.from_provider(
            [{"role": "assistant", "parts": [part]}]
        )


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


def test_to_image_part_unsupported_image():
    with pytest.raises(
        ValueError,
        match="Unsupported image media type: application/json. Expected one of: image/jpeg, image/png, image/gif, image/webp.",
    ):
        _to_image_part(mime_type="application/json", data=b"{}")


def test_to_document_part_unsupported_document():
    with pytest.raises(
        ValueError,
        match="Unsupported document media type: application/json. Only application/pdf is supported.",
    ):
        _to_document_part(mime_type="application/json", data=b"{}")


def test_to_audio_part_supported():
    """Test _to_audio_part with a supported audio mime type."""
    result = _to_audio_part(mime_type="audio/mp3", data=b"audio")
    assert isinstance(result, AudioPart)
    assert result.media_type == "audio/mp3"
    assert result.audio == b"audio"


def test_to_audio_part_unsupported():
    with pytest.raises(
        ValueError,
        match="Unsupported audio media type: application/json. Expected one of: audio/wav, audio/mp3, audio/aiff, audio/aac, audio/ogg, audio/flac.",
    ):
        _to_audio_part(mime_type="application/json", data=b"{}")


def test_to_provider():
    results = GeminiMessageParamConverter.to_provider(
        [BaseMessageParam(role="assistant", content="Hello")]
    )
    assert results == [{"parts": ["Hello"], "role": "model"}]


def test_inline_data_application_pdf():
    part = protos.Part(
        inline_data=protos.Blob(mime_type="application/pdf", data=b"%PDF-1.4...")
    )
    results = GeminiMessageParamConverter.from_provider(
        [{"role": "assistant", "parts": [part]}]
    )
    assert len(results) == 1
    result = results[0]
    assert isinstance(result.content, list)
    assert len(result.content) == 1
    assert isinstance(result.content[0], DocumentPart)
    assert result.content[0].media_type == "application/pdf"
    assert result.content[0].document == b"%PDF-1.4..."


def test_function_response():
    part = protos.Part(
        function_response=protos.FunctionResponse(
            name="some_tool", response={"result": "value"}
        )
    )
    results = GeminiMessageParamConverter.from_provider(
        [{"role": "assistant", "parts": [part]}]
    )
    assert len(results) == 1
    assert results == [
        BaseMessageParam(
            role="assistant",
            content=[
                ToolResultPart(
                    type="tool_result",
                    name="some_tool",
                    content="value",
                    id=None,
                    is_error=False,
                )
            ],
        )
    ]


def test_protos_function_response():
    part = protos.FunctionResponse(name="some_tool", response={"result": "value"})

    results = GeminiMessageParamConverter.from_provider(
        [{"role": "assistant", "parts": [part]}]
    )
    assert len(results) == 1
    assert results == [
        BaseMessageParam(
            role="assistant",
            content=[
                ToolResultPart(
                    type="tool_result",
                    name="some_tool",
                    content="value",
                    id=None,
                    is_error=False,
                )
            ],
        )
    ]


def test_protos_function_call():
    part = protos.FunctionCall(name="some_tool", args={"param1": "value1"})

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


def test_gemini_convert_parts_file_data_image():
    """
    When a part has file_data with an image mime type, it should produce an ImageURLPart.
    """
    file_data = protos.FileData(
        mime_type="image/jpeg", file_uri="http://example.com/img"
    )
    part = protos.Part(file_data=file_data)
    results = GeminiMessageParamConverter.from_provider(
        [{"role": "assistant", "parts": [part]}]
    )
    assert len(results) == 1
    result = results[0]
    assert isinstance(result.content, list)
    assert len(result.content) == 1
    assert isinstance(result.content[0], ImageURLPart)
    assert result.content[0].url == "http://example.com/img"


def test_gemini_convert_parts_file_data_audio():
    """
    When a part has file_data with an audio mime type, it should produce an AudioURLPart.
    """
    file_data = protos.FileData(
        mime_type="audio/mp3", file_uri="http://example.com/audio"
    )
    part = protos.Part(file_data=file_data)
    results = GeminiMessageParamConverter.from_provider(
        [{"role": "assistant", "parts": [part]}]
    )
    assert len(results) == 1
    result = results[0]
    assert isinstance(result.content, list)
    assert len(result.content) == 1
    assert isinstance(result.content[0], AudioURLPart)
    assert result.content[0].url == "http://example.com/audio"


def test_gemini_convert_parts_file_data_unsupported():
    """
    When a part has file_data with an unsupported mime type, the converter should raise ValueError.
    """
    file_data = protos.FileData(
        mime_type="application/zip", file_uri="http://example.com/zip"
    )
    part = protos.Part(file_data=file_data)
    with pytest.raises(
        ValueError,
        match="Unsupported file_data mime type: application/zip. Cannot convert to BaseMessageParam.",
    ):
        GeminiMessageParamConverter.from_provider(
            [{"role": "assistant", "parts": [part]}]
        )
