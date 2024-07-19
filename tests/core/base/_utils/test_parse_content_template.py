"""Tests the `_utils.parse_content_template` function."""

from unittest.mock import MagicMock, patch

import pytest

from mirascope.core.base._utils.parse_content_template import parse_content_template


def test_parse_content_template() -> None:
    """Test the parse_content_template function."""
    assert parse_content_template("user", "", {}) is None
    template = "This is a {var1} template with {var2} variables."
    values = {"var1": "test", "var2": "two"}
    expected = {
        "role": "user",
        "content": [
            {"type": "text", "text": "This is a test template with two variables."}
        ],
    }
    assert parse_content_template("user", template, values) == expected

    with pytest.raises(ValueError, match="Template type 'unknown' not supported."):
        parse_content_template("user", "{unknown:url}", {})


@patch("mirascope.core.base._utils.parse_content_template.open", new_callable=MagicMock)
@patch("urllib.request.urlopen", new_callable=MagicMock)
def test_parse_content_template_images(
    mock_urlopen: MagicMock, mock_open: MagicMock
) -> None:
    """Test the parse_content_template function with image templates."""
    image_data = b"\xff\xd8\xffimage data"
    mock_response = MagicMock()
    setattr(mock_response, "read", lambda: image_data)
    mock_urlopen.return_value.__enter__.return_value = mock_response
    mock_open.return_value.__enter__.return_value = mock_response
    template = "Analyze this image: {image:url}"
    expected = {
        "role": "user",
        "content": [
            {"type": "text", "text": "Analyze this image:"},
            {
                "type": "image",
                "media_type": "image/jpeg",
                "image": image_data,
                "detail": None,
            },
        ],
    }
    assert parse_content_template("user", template, {"url": "https://"}) == expected
    assert parse_content_template("user", template, {"url": "./image.jpg"}) == expected
    assert parse_content_template("user", template, {"url": image_data}) == expected

    template = "Analyze this image: {image:url,detail:low}"
    expected = {
        "role": "user",
        "content": [
            {"type": "text", "text": "Analyze this image:"},
            {
                "type": "image",
                "media_type": "image/jpeg",
                "image": image_data,
                "detail": "low",
            },
        ],
    }
    assert parse_content_template("user", template, {"url": "https://"}) == expected

    with pytest.raises(ValueError, match="Invalid detail value: standard"):
        parse_content_template(
            "user", "{image:url,detail:standard}", {"url": "https://"}
        )

    template = "Analyze these images: {images:urls}"
    expected = {
        "role": "user",
        "content": [
            {"type": "text", "text": "Analyze these images:"},
            {
                "type": "image",
                "media_type": "image/jpeg",
                "image": image_data,
                "detail": None,
            },
            {
                "type": "image",
                "media_type": "image/jpeg",
                "image": image_data,
                "detail": None,
            },
        ],
    }
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


@patch("mirascope.core.base._utils.parse_content_template.open", new_callable=MagicMock)
@patch("urllib.request.urlopen", new_callable=MagicMock)
def test_parse_content_template_audio(
    mock_urlopen: MagicMock, mock_open: MagicMock
) -> None:
    """Test the parse_content_template function with image templates."""
    audio_data = b"ID3audio data"
    mock_response = MagicMock()
    setattr(mock_response, "read", lambda: audio_data)
    mock_urlopen.return_value.__enter__.return_value = mock_response
    mock_open.return_value.__enter__.return_value = mock_response
    template = "Analyze this audio: {audio:url}"
    expected = {
        "role": "user",
        "content": [
            {"type": "text", "text": "Analyze this audio:"},
            {
                "type": "audio",
                "media_type": "audio/mp3",
                "audio": audio_data,
            },
        ],
    }
    assert parse_content_template("user", template, {"url": "https://"}) == expected
    assert parse_content_template("user", template, {"url": "./audio.mp3"}) == expected
    assert parse_content_template("user", template, {"url": audio_data}) == expected

    template = "Analyze these audio files: {audios:urls}"
    expected = {
        "role": "user",
        "content": [
            {"type": "text", "text": "Analyze these audio files:"},
            {
                "type": "audio",
                "media_type": "audio/mp3",
                "audio": audio_data,
            },
            {
                "type": "audio",
                "media_type": "audio/mp3",
                "audio": audio_data,
            },
        ],
    }
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
