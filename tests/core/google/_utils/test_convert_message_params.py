"""Tests the `google._utils.convert_message_params` function."""

from unittest.mock import MagicMock, patch

import pytest
from google.genai.types import ContentDict

from mirascope.core.base import (
    AudioPart,
    AudioURLPart,
    BaseMessageParam,
    CacheControlPart,
    ImagePart,
    ImageURLPart,
    TextPart,
)
from mirascope.core.google._utils._convert_message_params import convert_message_params


@patch("PIL.Image.open", new_callable=MagicMock)
def test_convert_message_params(mock_image_open: MagicMock) -> None:
    """Tests the `convert_message_params` function."""
    mock_image_open.return_value = "test"
    message_params: list[BaseMessageParam | ContentDict] = [
        BaseMessageParam(role="system", content="You are a helpful assistant."),
        BaseMessageParam(role="user", content="Hello"),
        {"role": "user", "parts": ["Hello", {"type": "text", "text": "Hello"}]},  # pyright: ignore[reportAssignmentType]
        BaseMessageParam(
            role="user",
            content=[
                TextPart(type="text", text="test"),
                ImagePart(
                    type="image", media_type="image/jpeg", image=b"image", detail=None
                ),
                AudioPart(type="audio", media_type="audio/wav", audio=b"audio"),
            ],
        ),
    ]
    mock_client = MagicMock()
    converted_message_params = convert_message_params(message_params, mock_client)
    assert converted_message_params == [
        {"parts": [{"text": "You are a helpful assistant."}], "role": "system"},
        {"parts": [{"text": "Hello"}], "role": "user"},
        {"parts": ["Hello", {"text": "Hello", "type": "text"}], "role": "user"},
        {
            "parts": [
                {"text": "test"},
                {"inline_data": {"data": b"image", "mime_type": "image/jpeg"}},
                {"inline_data": {"data": b"audio", "mime_type": "audio/wav"}},
            ],
            "role": "user",
        },
    ]

    with pytest.raises(
        ValueError,
        match="Unsupported image media type: image/svg. Google currently only supports "
        "JPEG, PNG, WebP, HEIC, and HEIF images.",
    ):
        convert_message_params(
            [
                BaseMessageParam(
                    role="user",
                    content=[
                        ImagePart(
                            type="image",
                            media_type="image/svg",
                            image=b"image",
                            detail=None,
                        )
                    ],
                ),
            ],
            mock_client,
        )

    with pytest.raises(
        ValueError,
        match="Unsupported audio media type: audio/unknown. "
        "Google currently only supports WAV, MP3, AIFF, AAC, OGG, "
        "and FLAC audio file types.",
    ):
        convert_message_params(
            [
                BaseMessageParam(
                    role="user",
                    content=[
                        AudioPart(
                            type="audio", media_type="audio/unknown", audio=b"audio"
                        )
                    ],
                ),
            ],
            mock_client,
        )

    with pytest.raises(
        ValueError,
        match="Google currently only supports text, image, and audio parts. Part provided: cache_control",
    ):
        convert_message_params(
            [
                BaseMessageParam(
                    role="user",
                    content=[
                        CacheControlPart(type="cache_control", cache_type="ephemeral")
                    ],
                )
            ],
            mock_client,
        )


@patch(
    "mirascope.core.google._utils._convert_message_params._load_media",
    return_value=b"image_url_data",
)
@patch("PIL.Image.open", new_callable=MagicMock)
def test_image_url_with_http_valid(
    mock_image_open: MagicMock, mock_load_media: MagicMock
) -> None:
    """Test image_url part with an HTTP URL and valid media type."""
    fake_image = MagicMock()
    fake_image.format = "PNG"
    mock_image_open.return_value = fake_image

    message = BaseMessageParam(
        role="user",
        content=[
            ImageURLPart(type="image_url", url="https://example.com/image", detail=None)
        ],
    )
    result = convert_message_params([message], MagicMock())
    # Expect the image to be processed via PIL.Image.open and returned in parts.
    assert result == [
        {
            "parts": [
                {
                    "file_data": {
                        "file_uri": "https://example.com/image",
                        "mime_type": "image/png",
                    }
                }
            ],
            "role": "user",
        }
    ]
    # Check that _load_media was called with the URL.
    mock_load_media.assert_called_once_with("https://example.com/image")


@patch(
    "mirascope.core.google._utils._convert_message_params._load_media",
    return_value=b"image_url_data",
)
@patch("PIL.Image.open", new_callable=MagicMock)
def test_image_url_with_http_valid_gemini(
    mock_image_open: MagicMock, mock_load_media: MagicMock
) -> None:
    """Test image_url part with an HTTP URL and valid media type."""
    fake_image = MagicMock()
    fake_image.format = "PNG"
    mock_image_open.return_value = fake_image

    message = BaseMessageParam(
        role="user",
        content=[
            ImageURLPart(type="image_url", url="https://example.com/image", detail=None)
        ],
    )
    mock_client = MagicMock()
    mock_client.vertexai = False
    mock_file = MagicMock(uri="file://local/path/image", mime_type="image/jpeg")
    mock_client.files.upload.return_value = mock_file
    result = convert_message_params([message], mock_client)
    # Expect the image to be processed via PIL.Image.open and returned in parts.
    assert result == [
        {
            "parts": [
                {
                    "file_data": {
                        "file_uri": "file://local/path/image",
                        "mime_type": "image/jpeg",
                    }
                }
            ],
            "role": "user",
        }
    ]
    # Check that _load_media was called with the URL.
    mock_load_media.assert_called_once_with("https://example.com/image")


@patch(
    "mirascope.core.google._utils._convert_message_params._load_media",
    return_value=b"image_url_data",
)
@patch("PIL.Image.open", new_callable=MagicMock)
def test_image_url_with_http_invalid_media_type(
    mock_image_open: MagicMock, mock_load_media: MagicMock
) -> None:
    """Test image_url part with an HTTP URL and an invalid media type raises ValueError."""
    # Use patch.dict to temporarily set PIL.Image.MIME for an invalid format.
    with patch.dict("PIL.Image.MIME", {"SVG": "image/svg"}, clear=False):
        fake_image = MagicMock()
        fake_image.format = "SVG"
        mock_image_open.return_value = fake_image

        message = BaseMessageParam(
            role="user",
            content=[
                ImageURLPart(
                    type="image_url", url="https://example.com/image", detail=None
                )
            ],
        )
        with pytest.raises(
            ValueError,
            match="Unsupported image media type: image/svg. Google currently only supports JPEG, PNG, WebP, HEIC, and HEIF images.",
        ):
            convert_message_params([message], MagicMock())


@patch("mirascope.core.google._utils._convert_message_params._load_media")
def test_image_url_with_non_http(mock_load_media: MagicMock) -> None:
    """Test image_url part with a non-HTTP URL returns a FileData object."""
    # For non-HTTP URLs, _load_media should not be called.
    message = BaseMessageParam(
        role="user",
        content=[
            ImageURLPart(type="image_url", url="file://local/path/image", detail=None)
        ],
    )
    result = convert_message_params([message], MagicMock())
    # Expect the part to be a FileData with file_uri equal to the URL.
    assert len(result) == 1
    assert "parts" in result[0]
    assert result[0]["parts"]
    part = result[0]["parts"][0]
    assert isinstance(part, dict)
    assert part == {
        "file_data": {
            "file_uri": "file://local/path/image",
            "mime_type": None,
        }
    }
    mock_load_media.assert_not_called()


@patch(
    "mirascope.core.google._utils._convert_message_params._load_media",
    return_value=b"audio_data",
)
@patch(
    "mirascope.core.google._utils._convert_message_params.get_audio_type",
    return_value="audio/wav",
)
def test_audio_url_with_http_valid(
    mock_get_audio_type: MagicMock, mock_load_media: MagicMock
) -> None:
    """Test audio_url part with an HTTP URL and a valid audio type."""
    message = BaseMessageParam(
        role="user",
        content=[AudioURLPart(type="audio_url", url="https://example.com/audio")],
    )
    result = convert_message_params([message], MagicMock())
    assert result == [
        {
            "parts": [
                {
                    "file_data": {
                        "file_uri": "https://example.com/audio",
                        "mime_type": "audio/wav",
                    }
                },
            ],
            "role": "user",
        }
    ]
    mock_load_media.assert_called_once_with("https://example.com/audio")
    mock_get_audio_type.assert_called_once_with(b"audio_data")


@patch(
    "mirascope.core.google._utils._convert_message_params._load_media",
    return_value=b"audio_data",
)
@patch(
    "mirascope.core.google._utils._convert_message_params.get_audio_type",
    return_value="audio/unknown",
)
def test_audio_url_with_http_invalid(
    mock_get_audio_type: MagicMock, mock_load_media: MagicMock
) -> None:
    """Test audio_url part with an HTTP URL and an invalid audio type raises ValueError."""
    message = BaseMessageParam(
        role="user",
        content=[AudioURLPart(type="audio_url", url="https://example.com/audio")],
    )
    with pytest.raises(
        ValueError,
        match="Unsupported audio media type: audio/unknown. Google currently only supports WAV, MP3, AIFF, AAC, OGG, and FLAC audio file types.",
    ):
        convert_message_params([message], MagicMock())
    mock_load_media.assert_called_once_with("https://example.com/audio")
    mock_get_audio_type.assert_called_once_with(b"audio_data")


def test_audio_url_with_non_http() -> None:
    """Test audio_url part with a non-HTTP URL returns a FileData object."""
    message = BaseMessageParam(
        role="user",
        content=[AudioURLPart(type="audio_url", url="ftp://example.com/audio")],
    )
    result = convert_message_params([message], MagicMock())
    assert len(result) == 1
    assert "parts" in result[0]
    assert result[0]["parts"]
    part = result[0]["parts"][0]
    assert isinstance(part, dict)
    assert part == {
        "file_data": {
            "file_uri": "ftp://example.com/audio",
            "mime_type": None,
        }
    }
