from unittest.mock import MagicMock, patch

import pytest
from google.genai.types import (
    BlobDict,
    FileDataDict,
    FunctionCallDict,
    FunctionResponseDict,
    PartDict,
)

from mirascope.core import BaseMessageParam
from mirascope.core.base import (
    AudioURLPart,
    DocumentPart,
    ImagePart,
    ImageURLPart,
    ToolCallPart,
    ToolResultPart,
)
from mirascope.core.google._utils._message_param_converter import (
    GoogleMessageParamConverter,
)


def test_google_convert_parts_text_only():
    """
    If parts contain only text, the converter should produce
    a BaseMessageParam with either a single text string or a list[TextPart].
    """
    part = PartDict(text="hello world")
    results = GoogleMessageParamConverter.from_provider(
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


def test_google_convert_parts_image():
    """
    If inline_data has an image mime type, produce an ImagePart.
    """
    part = PartDict(
        inline_data=BlobDict(mime_type="image/png", data=b"\x89PNG\r\n\x1a\n")
    )
    results = GoogleMessageParamConverter.from_provider(
        [{"role": "assistant", "parts": [part]}]
    )
    assert len(results) == 1
    result = results[0]
    assert isinstance(result.content, list)
    assert len(result.content) == 1
    assert isinstance(result.content[0], ImagePart)
    assert result.content[0].media_type == "image/png"
    assert result.content[0].image == b"\x89PNG\r\n\x1a\n"


def test_google_convert_parts_document():
    """
    If file_data is a PDF, produce a DocumentPart.
    """
    part = PartDict(
        file_data=FileDataDict(mime_type="application/pdf", file_uri="%PDF-1.4...")
    )
    converted_message = GoogleMessageParamConverter.from_provider(
        [{"role": "assistant", "parts": [part]}]
    )[0]
    assert isinstance(converted_message.content[0], ImageURLPart)


def test_google_convert_parts_unsupported_image():
    """
    If inline_data has an unsupported image type (e.g. image/tiff),
    the converter should raise ValueError.
    """
    part = PartDict(inline_data=BlobDict(mime_type="image/tiff", data=b"fake"))
    with pytest.raises(
        ValueError,
        match="Unsupported image media type: image/tiff. Google currently only supports JPEG, PNG, WebP, HEIC, and HEIF images.",
    ):
        GoogleMessageParamConverter.from_provider(
            [{"role": "assistant", "parts": [part]}]
        )


def test_google_convert_function_call():
    """
    If the part has a function_call, the converter returns a new BaseMessageParam
    with a ToolCallPart inside.
    """
    part = PartDict(
        function_call=FunctionCallDict(name="some_tool", args={"param1": "value1"})
    )
    results = GoogleMessageParamConverter.from_provider(
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


def test_google_convert_no_supported_content():
    """
    If none of text, inline_data, file_data, function_call, or function_response
    is set, the converter should raise ValueError.
    """
    part = PartDict()
    # No text, no inline_data, no file_data, no function_call, no function_response
    with pytest.raises(
        ValueError,
        match="Part does not contain any supported content \\(text, image, or document\\).",
    ):
        GoogleMessageParamConverter.from_provider(
            [{"role": "assistant", "parts": [part]}]
        )


@patch(
    "mirascope.core.google._utils._message_param_converter.Client",
    new_callable=MagicMock,
)
def test_to_provider(mock_client_class):
    results = GoogleMessageParamConverter.to_provider(
        [BaseMessageParam(role="assistant", content="Hello")]
    )
    assert results == [{"parts": [{"text": "Hello"}], "role": "model"}]
    mock_client_class.assert_called_once_with()


def test_inline_data_audio():
    part = PartDict(
        inline_data=BlobDict(mime_type="audio/mp3", data=b"fake audio data")
    )
    results = GoogleMessageParamConverter.from_provider(
        [{"role": "assistant", "parts": [part]}]
    )
    assert len(results) == 1
    result = results[0]
    assert isinstance(result.content, list)
    assert len(result.content) == 1
    assert result.content[0].model_dump() == {
        "type": "audio",
        "media_type": "audio/mp3",
        "audio": b"fake audio data",
    }


def test_inline_data_application_pdf():
    part = PartDict(
        inline_data=BlobDict(mime_type="application/pdf", data=b"%PDF-1.4...")
    )
    results = GoogleMessageParamConverter.from_provider(
        [{"role": "assistant", "parts": [part]}]
    )
    assert len(results) == 1
    result = results[0]
    assert isinstance(result.content, list)
    assert len(result.content) == 1
    assert isinstance(result.content[0], DocumentPart)
    assert result.content[0].media_type == "application/pdf"
    assert result.content[0].document == b"%PDF-1.4..."


def test_inline_data_unknown_mime_type():
    part = PartDict(
        inline_data=BlobDict(mime_type="application/zip", data=b"fake zip data")
    )
    with pytest.raises(
        ValueError,
        match="Unsupported inline_data mime type: application/zip. Cannot convert to BaseMessageParam.",
    ):
        GoogleMessageParamConverter.from_provider(
            [{"role": "assistant", "parts": [part]}]
        )


def test_function_response():
    part = PartDict(
        function_response=FunctionResponseDict(
            name="some_tool", response={"content": "value"}
        )
    )
    results = GoogleMessageParamConverter.from_provider(
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


def test_google_convert_parts_file_data_image():
    """
    When a part has file_data with an image mime type, it should produce an ImageURLPart.
    """
    file_data = FileDataDict(mime_type="image/jpeg", file_uri="http://example.com/img")
    part = PartDict(file_data=file_data)
    results = GoogleMessageParamConverter.from_provider(
        [{"role": "assistant", "parts": [part]}]
    )
    assert len(results) == 1
    result = results[0]
    assert isinstance(result.content, list)
    assert len(result.content) == 1
    assert isinstance(result.content[0], ImageURLPart)
    assert result.content[0].url == "http://example.com/img"


def test_google_convert_parts_file_data_audio():
    """
    When a part has file_data with an audio mime type, it should produce an AudioURLPart.
    """
    file_data = FileDataDict(mime_type="audio/mp3", file_uri="http://example.com/audio")
    part = PartDict(file_data=file_data)
    results = GoogleMessageParamConverter.from_provider(
        [{"role": "assistant", "parts": [part]}]
    )
    assert len(results) == 1
    result = results[0]
    assert isinstance(result.content, list)
    assert len(result.content) == 1
    assert isinstance(result.content[0], AudioURLPart)
    assert result.content[0].url == "http://example.com/audio"


def test_google_convert_parts_file_data_unknown_mime_type():
    """When a part has file_data with an unknown mime type, it should use ImageURLPart."""
    file_data = FileDataDict(
        mime_type="application/zip",
        file_uri="http://generativelanguage.googleapis.com/files/zip",
    )
    part = PartDict(file_data=file_data)
    converted_message = GoogleMessageParamConverter.from_provider(
        [{"role": "assistant", "parts": [part]}]
    )[0]
    assert isinstance(converted_message.content[0], ImageURLPart)
