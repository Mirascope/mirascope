"""Tests the `_utils.parse_content_template` function."""

from unittest.mock import MagicMock, patch

import pytest

from mirascope.core.base._utils._parse_content_template import parse_content_template
from mirascope.core.base.message_param import (
    AudioPart,
    BaseMessageParam,
    CacheControlPart,
    DocumentPart,
    ImagePart,
    TextPart,
)


def test_parse_content_template() -> None:
    """Test the parse_content_template function."""
    assert parse_content_template("user", "", {}) is None
    assert parse_content_template("user", " ", {}) is None
    assert parse_content_template("system", "", {}) is None
    template = "This is a {var1} template with {var2} variables."
    values = {"var1": "test", "var2": "two"}
    expected = BaseMessageParam(
        role="user", content="This is a test template with two variables."
    )
    assert parse_content_template("user", template, values) == expected


@patch(
    "mirascope.core.base._utils._parse_content_template.open", new_callable=MagicMock
)
@patch("urllib.request.urlopen", new_callable=MagicMock)
def test_parse_content_template_images(
    mock_urlopen: MagicMock, mock_open: MagicMock
) -> None:
    """Test the parse_content_template function with image templates."""
    image_data = b"\xff\xd8\xffimage data"
    mock_response = MagicMock()
    mock_response.read = lambda: image_data
    mock_urlopen.return_value.__enter__.return_value = mock_response
    mock_open.return_value.__enter__.return_value = mock_response
    template = "Analyze this image: {url:image}"
    expected = BaseMessageParam(
        role="user",
        content=[
            TextPart(type="text", text="Analyze this image:"),
            ImagePart(
                type="image", media_type="image/jpeg", image=image_data, detail=None
            ),
        ],
    )
    assert parse_content_template("user", template, {"url": "https://"}) == expected
    assert parse_content_template("user", template, {"url": "./image.jpg"}) == expected
    assert parse_content_template("user", template, {"url": image_data}) == expected

    template = "Analyze this image: {url:image(detail=low)}"
    expected = BaseMessageParam(
        role="user",
        content=[
            TextPart(type="text", text="Analyze this image:"),
            ImagePart(
                type="image", media_type="image/jpeg", image=image_data, detail="low"
            ),
        ],
    )
    assert parse_content_template("user", template, {"url": "https://"}) == expected

    template = "Analyze these images: {urls:images}"
    expected = BaseMessageParam(
        role="user",
        content=[
            TextPart(type="text", text="Analyze these images:"),
            ImagePart(
                type="image", media_type="image/jpeg", image=image_data, detail=None
            ),
            ImagePart(
                type="image", media_type="image/jpeg", image=image_data, detail=None
            ),
        ],
    )
    assert (
        parse_content_template("user", template, {"urls": ["https://", "https://."]})
        == expected
    )
    assert (
        parse_content_template(
            "user", template, {"urls": ["./image.jpg", "./image.jpg"]}
        )
        == expected
    )
    assert (
        parse_content_template("user", template, {"urls": [image_data, image_data]})
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
            AudioPart(type="audio", media_type="audio/mp3", audio=audio_data),
        ],
    )
    assert parse_content_template("user", template, {"url": "https://"}) == expected
    assert parse_content_template("user", template, {"url": "./audio.mp3"}) == expected
    assert parse_content_template("user", template, {"url": audio_data}) == expected

    template = "Analyze these audio files: {urls:audios}"
    expected = BaseMessageParam(
        role="user",
        content=[
            TextPart(type="text", text="Analyze these audio files:"),
            AudioPart(type="audio", media_type="audio/mp3", audio=audio_data),
            AudioPart(type="audio", media_type="audio/mp3", audio=audio_data),
        ],
    )
    assert (
        parse_content_template("user", template, {"urls": ["https://", "https://."]})
        == expected
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
