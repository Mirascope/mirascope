"""Tests the `_utils.parse_content_template` function."""

from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from mirascope.core.base._utils._parse_content_template import parse_content_template
from mirascope.core.base.message_param import (
    AudioPart,
    AudioURLPart,
    BaseMessageParam,
    CacheControlPart,
    DocumentPart,
    ImagePart,
    ImageURLPart,
    TextPart,
)


def test_parse_content_template() -> None:
    """Test the parse_content_template function."""
    assert parse_content_template("user", "", {}) is None
    assert parse_content_template("user", " ", {}) is None
    assert parse_content_template("system", "", {}) is None
    assert parse_content_template("system", " \u200b ", {}) is None
    template = "This is a {var1} template with {var2} variables."
    values = {"var1": "test", "var2": "two"}
    expected = BaseMessageParam(
        role="user", content="This is a test template with two variables."
    )
    assert parse_content_template("user", template, values) == expected


@pytest.fixture
def mock_jpeg_bytes() -> bytes:
    return b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07\"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xf9\xfe\xbf\xff\xd9"


@patch(
    "mirascope.core.base._utils._parse_content_template.open", new_callable=MagicMock
)
@patch("urllib.request.urlopen", new_callable=MagicMock)
def test_parse_content_template_images(
    mock_urlopen: MagicMock, mock_open: MagicMock, mock_jpeg_bytes: bytes
) -> None:
    """Test the parse_content_template function with image templates."""
    mock_response = MagicMock()
    mock_response.read = lambda: mock_jpeg_bytes
    mock_urlopen.return_value.__enter__.return_value = mock_response
    mock_open.return_value.__enter__.return_value = mock_response
    template = "Analyze this image: {url:image}"
    expected = BaseMessageParam(
        role="user",
        content=[
            TextPart(type="text", text="Analyze this image:"),
            ImageURLPart(type="image_url", url="https://", detail=None),
        ],
    )
    assert parse_content_template("user", template, {"url": "https://"}) == expected
    expected = BaseMessageParam(
        role="user",
        content=[
            TextPart(type="text", text="Analyze this image:"),
            ImagePart(
                type="image",
                media_type="image/jpeg",
                image=mock_jpeg_bytes,
                detail=None,
            ),
        ],
    )
    assert parse_content_template("user", template, {"url": "./image.jpg"}) == expected
    assert (
        parse_content_template("user", template, {"url": mock_jpeg_bytes}) == expected
    )
    assert (
        parse_content_template(
            "user", template, {"url": Image.open(BytesIO(mock_jpeg_bytes))}
        )
        == expected
    )

    template = "Analyze this image: {url:image(detail=low)}"
    expected = BaseMessageParam(
        role="user",
        content=[
            TextPart(type="text", text="Analyze this image:"),
            ImageURLPart(type="image_url", url="https://", detail="low"),
        ],
    )
    assert parse_content_template("user", template, {"url": "https://"}) == expected

    template = "Analyze these images: {urls:images}"
    expected = BaseMessageParam(
        role="user",
        content=[
            TextPart(type="text", text="Analyze these images:"),
            ImageURLPart(type="image_url", url="https://", detail=None),
            ImageURLPart(type="image_url", url="https://.", detail=None),
        ],
    )
    assert (
        parse_content_template("user", template, {"urls": ["https://", "https://."]})
        == expected
    )
    expected = expected = BaseMessageParam(
        role="user",
        content=[
            TextPart(type="text", text="Analyze these images:"),
            ImagePart(
                type="image",
                media_type="image/jpeg",
                image=mock_jpeg_bytes,
                detail=None,
            ),
            ImagePart(
                type="image",
                media_type="image/jpeg",
                image=mock_jpeg_bytes,
                detail=None,
            ),
        ],
    )
    assert (
        parse_content_template(
            "user", template, {"urls": ["./image.jpg", "./image.jpg"]}
        )
        == expected
    )
    assert (
        parse_content_template(
            "user", template, {"urls": [mock_jpeg_bytes, mock_jpeg_bytes]}
        )
        == expected
    )

    with pytest.raises(
        ValueError,
        match="When using 'images' template, 'urls' must be a list.",
    ):
        parse_content_template("user", template, {"urls": None})


@patch(
    "mirascope.core.base._utils._parse_content_template.open", new_callable=MagicMock
)
@patch("urllib.request.urlopen", new_callable=MagicMock)
def test_parse_content_template_audio(
    mock_urlopen: MagicMock, mock_open: MagicMock
) -> None:
    """Test the parse_content_template function with image templates."""
    audio_data = b"ID3audio data"
    mock_response = MagicMock()
    mock_response.read = lambda: audio_data
    mock_urlopen.return_value.__enter__.return_value = mock_response
    mock_open.return_value.__enter__.return_value = mock_response
    template = "Analyze this audio: {url:audio}"
    expected = BaseMessageParam(
        role="user",
        content=[
            TextPart(type="text", text="Analyze this audio:"),
            AudioURLPart(type="audio_url", url="https://"),
        ],
    )
    assert parse_content_template("user", template, {"url": "https://"}) == expected
    expected = BaseMessageParam(
        role="user",
        content=[
            TextPart(type="text", text="Analyze this audio:"),
            AudioPart(type="audio", media_type="audio/mp3", audio=audio_data),
        ],
    )
    assert parse_content_template("user", template, {"url": "./audio.mp3"}) == expected
    assert parse_content_template("user", template, {"url": audio_data}) == expected

    template = "Analyze these audio files: {urls:audios}"

    expected = BaseMessageParam(
        role="user",
        content=[
            TextPart(type="text", text="Analyze these audio files:"),
            AudioURLPart(type="audio_url", url="https://"),
            AudioURLPart(type="audio_url", url="https://."),
        ],
    )
    assert (
        parse_content_template("user", template, {"urls": ["https://", "https://."]})
        == expected
    )
    expected = BaseMessageParam(
        role="user",
        content=[
            TextPart(type="text", text="Analyze these audio files:"),
            AudioPart(type="audio", media_type="audio/mp3", audio=audio_data),
            AudioPart(type="audio", media_type="audio/mp3", audio=audio_data),
        ],
    )
    assert (
        parse_content_template(
            "user", template, {"urls": ["./audio.mp3", "./audio.mp3"]}
        )
        == expected
    )
    assert (
        parse_content_template("user", template, {"urls": [audio_data, audio_data]})
        == expected
    )

    with pytest.raises(
        ValueError,
        match="When using 'audios' template, 'urls' must be a list.",
    ):
        parse_content_template("user", template, {"urls": None})


def test_parse_content_template_cache_control() -> None:
    """Test the parse_content_template function with a cache_control part."""
    expected = BaseMessageParam(
        role="user",
        content=[CacheControlPart(type="cache_control", cache_type="ephemeral")],
    )
    assert parse_content_template("user", "{:cache_control}", {}) == expected
    assert (
        parse_content_template("user", "{:cache_control(type=ephemeral)}", {})
        == expected
    )
    assert parse_content_template("user", "{not_used:cache_control}", {}) == expected

    expected.role = "system"
    assert parse_content_template("system", "{:cache_control}", {}) == expected


def test_parse_content_template_texts() -> None:
    """Test the parse_content_template function with text templates."""
    # Test single text template
    template = "Process this text: {content:text}"
    expected = BaseMessageParam(
        role="user",
        content=[
            TextPart(type="text", text="Process this text:"),
            TextPart(type="text", text="Hello world"),
        ],
    )
    assert (
        parse_content_template("user", template, {"content": "Hello world"}) == expected
    )

    # Test texts template with list
    template = "Process these texts: {content:texts}"
    expected = BaseMessageParam(
        role="user",
        content=[
            TextPart(type="text", text="Process these texts:"),
            TextPart(type="text", text="Hello"),
            TextPart(type="text", text="world"),
        ],
    )
    assert (
        parse_content_template("user", template, {"content": ["Hello", "world"]})
        == expected
    )

    # Test empty list
    assert parse_content_template(
        "user", template, {"content": []}
    ) == BaseMessageParam(role="user", content="Process these texts:")

    # Test texts validation
    with pytest.raises(
        ValueError,
        match="When using 'texts' template, 'content' must be a list.",
    ):
        parse_content_template("user", template, {"content": "not a list"})

    # Test attribute access
    template = "Process this text: {attr:text}"
    assert parse_content_template(
        "user", template, {"attr": "value"}
    ) == BaseMessageParam(
        role="user",
        content=[
            TextPart(type="text", text="Process this text:"),
            TextPart(type="text", text="value"),
        ],
    )

    # Test empty text part
    assert parse_content_template("user", template, {"attr": ""}) == BaseMessageParam(
        role="user",
        content=[
            TextPart(type="text", text="Process this text:"),
            TextPart(type="text", text=""),
        ],
    )


@patch(
    "mirascope.core.base._utils._parse_content_template.open", new_callable=MagicMock
)
@patch("urllib.request.urlopen", new_callable=MagicMock)
def test_parse_content_template_document(
    mock_urlopen: MagicMock, mock_open: MagicMock
) -> None:
    """Test the parse_content_template function with document templates."""
    document_data = b"%PDFdocument data"  # Magic bytes for PDF files
    mock_response = MagicMock()
    mock_response.read = lambda: document_data
    mock_urlopen.return_value.__enter__.return_value = mock_response
    mock_open.return_value.__enter__.return_value = mock_response

    # Test single document input
    template = "Analyze this document: {url:document}"
    expected = BaseMessageParam(
        role="user",
        content=[
            TextPart(type="text", text="Analyze this document:"),
            DocumentPart(
                type="document",
                media_type="application/pdf",
                document=document_data,
            ),
        ],
    )
    assert parse_content_template("user", template, {"url": "https://"}) == expected
    assert parse_content_template("user", template, {"url": "./doc.pdf"}) == expected
    assert parse_content_template("user", template, {"url": document_data}) == expected

    # Test multiple document inputs
    template = "Analyze these documents: {urls:documents}"
    expected = BaseMessageParam(
        role="user",
        content=[
            TextPart(type="text", text="Analyze these documents:"),
            DocumentPart(
                type="document",
                media_type="application/pdf",
                document=document_data,
            ),
            DocumentPart(
                type="document",
                media_type="application/pdf",
                document=document_data,
            ),
        ],
    )
    assert (
        parse_content_template("user", template, {"urls": ["https://", "https://."]})
        == expected
    )
    assert (
        parse_content_template("user", template, {"urls": ["./doc.pdf", "./doc.pdf"]})
        == expected
    )
    assert (
        parse_content_template(
            "user", template, {"urls": [document_data, document_data]}
        )
        == expected
    )

    # Test error case for invalid input type
    with pytest.raises(
        ValueError,
        match="When using 'documents' template, 'urls' must be a list.",
    ):
        parse_content_template("user", template, {"urls": None})


@patch(
    "mirascope.core.base._utils._parse_content_template.open", new_callable=MagicMock
)
@patch("urllib.request.urlopen", new_callable=MagicMock)
def test_parse_content_template_parts(
    mock_urlopen: MagicMock, mock_open: MagicMock, mock_jpeg_bytes: bytes
) -> None:
    """Test the parse_content_template function with parts templates."""
    # Test single parts template
    template = "Process these parts: {content:parts}"
    mixed_parts = [
        TextPart(type="text", text="Hello world"),
        ImagePart(
            type="image",
            media_type="image/jpeg",
            image=mock_jpeg_bytes,
            detail=None,
        ),
        AudioPart(
            type="audio",
            media_type="audio/mp3",
            audio=b"audio_bytes",
        ),
    ]
    expected = BaseMessageParam(
        role="user",
        content=[
            TextPart(type="text", text="Process these parts:"),
            *mixed_parts,
        ],
    )
    assert (
        parse_content_template("user", template, {"content": mixed_parts}) == expected
    )

    # Test empty list
    assert parse_content_template(
        "user", template, {"content": []}
    ) == BaseMessageParam(role="user", content="Process these parts:")

    # Test parts validation
    with pytest.raises(
        ValueError,
        match="When using 'parts' template, 'content' must be a list.",
    ):
        parse_content_template("user", template, {"content": "not a list"})

    with pytest.raises(
        ValueError,
        match="When using 'parts' template, 'content' must be a list of valid content parts.",
    ):
        parse_content_template("user", template, {"content": ["invalid part"]})


@patch(
    "mirascope.core.base._utils._parse_content_template.open", new_callable=MagicMock
)
@patch("urllib.request.urlopen", new_callable=MagicMock)
def test_parse_content_template_part(
    mock_urlopen: MagicMock, mock_open: MagicMock
) -> None:
    """Test the parse_content_template function with a single part template."""
    # Test single part template
    template = "Process this part: {content:part}"
    text_part = TextPart(type="text", text="Hello world")
    expected = BaseMessageParam(
        role="user",
        content=[
            TextPart(type="text", text="Process this part:"),
            text_part,
        ],
    )
    assert parse_content_template("user", template, {"content": text_part}) == expected

    # Test validation
    with pytest.raises(
        ValueError,
        match="When using 'part' template, 'content' must be a valid content part.",
    ):
        parse_content_template("user", template, {"content": "not a part"})
