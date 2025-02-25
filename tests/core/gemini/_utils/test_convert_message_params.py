"""Tests the `gemini._utils.convert_message_params` function."""

import io
from unittest.mock import MagicMock, patch

import pytest
from google.generativeai import protos
from google.generativeai.types import ContentDict

from mirascope.core.base import (
    AudioPart,
    AudioURLPart,
    BaseMessageParam,
    CacheControlPart,
    ImagePart,
    ImageURLPart,
    TextPart,
    ToolCallPart,
    ToolResultPart,
)
from mirascope.core.gemini._utils._convert_message_params import convert_message_params


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
                ToolResultPart(
                    name="tool_name", id="tool_id", content="result", type="tool_result"
                ),
            ],
        ),
        BaseMessageParam(
            role="model",
            content=[
                TextPart(type="text", text="test"),
                ToolCallPart(type="tool_call", name="tool_name", args={"arg": "val"}),
            ],
        ),
    ]
    converted_message_params = convert_message_params(message_params)
    assert converted_message_params == [
        {"role": "system", "parts": ["You are a helpful assistant."]},
        {"role": "user", "parts": ["Hello"]},
        {"role": "user", "parts": ["Hello", {"type": "text", "text": "Hello"}]},
        {
            "role": "user",
            "parts": ["test", "test", {"mime_type": "audio/wav", "data": b"audio"}],
        },
        {
            "role": "user",
            "parts": [
                protos.FunctionResponse(
                    name="tool_name", response={"result": "result"}
                ),
            ],
        },
        {
            "role": "model",
            "parts": [
                "test",
                protos.FunctionCall(
                    name="tool_name",
                    args={"arg": "val"},
                ),
            ],
        },
    ]

    one_part = BaseMessageParam(
        role="user",
        content=[
            TextPart(type="text", text="test"),
        ],
    )
    converted_message_params = convert_message_params([one_part])
    assert converted_message_params == [{"parts": ["test"], "role": "user"}]

    mock_image_open.assert_called_once()
    bytes_io: io.BytesIO = mock_image_open.call_args.args[0]
    assert bytes_io.getvalue() == b"image"

    with pytest.raises(
        ValueError,
        match="Unsupported image media type: image/svg. Gemini currently only supports "
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
            ]
        )

    with pytest.raises(
        ValueError,
        match="Unsupported audio media type: audio/unknown. "
        "Gemini currently only supports WAV, MP3, AIFF, AAC, OGG, and FLAC audio file types.",
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
            ]
        )

    with pytest.raises(
        ValueError,
        match="Gemini currently only supports text, image, and audio parts. Part provided: cache_control",
    ):
        convert_message_params(
            [
                BaseMessageParam(
                    role="user",
                    content=[
                        CacheControlPart(type="cache_control", cache_type="ephemeral")
                    ],
                )
            ]
        )


def test_system_message_non_string_content() -> None:
    """Test that a system message with non-string content raises ValueError."""
    with pytest.raises(
        ValueError,
        match="System message content must be a single text string.",
    ):
        convert_message_params(
            [
                BaseMessageParam(
                    role="system",
                    content=[TextPart(type="text", text="not a string")],
                )
            ]
        )


@patch(
    "mirascope.core.gemini._utils._convert_message_params._load_media",
    return_value=b"image_url_data",
)
@patch("PIL.Image.open", new_callable=MagicMock)
def test_image_url_with_http_valid(
    mock_image_open: MagicMock, mock_load_media: MagicMock
) -> None:
    """Test image_url part with an HTTP URL and valid media type."""
    fake_image = MagicMock()
    fake_image.format = "JPEG"
    mock_image_open.return_value = fake_image

    message = BaseMessageParam(
        role="user",
        content=[
            ImageURLPart(type="image_url", url="https://example.com/image", detail=None)
        ],
    )
    result = convert_message_params([message])
    # Expect the image to be processed via PIL.Image.open and returned in parts.
    assert result == [{"role": "user", "parts": [fake_image]}]
    # Check that _load_media was called with the URL.
    mock_load_media.assert_called_once_with("https://example.com/image")


@patch(
    "mirascope.core.gemini._utils._convert_message_params._load_media",
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
            match="Unsupported image media type: image/svg. Gemini currently only supports JPEG, PNG, WebP, HEIC, and HEIF images.",
        ):
            convert_message_params([message])


@patch("mirascope.core.gemini._utils._convert_message_params._load_media")
def test_image_url_with_non_http(mock_load_media: MagicMock) -> None:
    """Test image_url part with a non-HTTP URL returns a FileData object."""
    # For non-HTTP URLs, _load_media should not be called.
    message = BaseMessageParam(
        role="user",
        content=[
            ImageURLPart(type="image_url", url="file://local/path/image", detail=None)
        ],
    )
    result = convert_message_params([message])
    # Expect the part to be a FileData with file_uri equal to the URL.
    assert len(result) == 1
    part = result[0]["parts"][0]
    assert isinstance(part, protos.FileData)
    assert part.file_uri == "file://local/path/image"
    mock_load_media.assert_not_called()


@patch(
    "mirascope.core.gemini._utils._convert_message_params._load_media",
    return_value=b"audio_data",
)
@patch(
    "mirascope.core.gemini._utils._convert_message_params.get_audio_type",
    return_value="wav",
)
def test_audio_url_with_http_valid(
    mock_get_audio_type: MagicMock, mock_load_media: MagicMock
) -> None:
    """Test audio_url part with an HTTP URL and a valid audio type."""
    message = BaseMessageParam(
        role="user",
        content=[AudioURLPart(type="audio_url", url="https://example.com/audio")],
    )
    result = convert_message_params([message])
    assert result == [
        {"role": "user", "parts": [{"mime_type": "audio/wav", "data": b"audio_data"}]}
    ]
    mock_load_media.assert_called_once_with("https://example.com/audio")
    mock_get_audio_type.assert_called_once_with(b"audio_data")


@patch(
    "mirascope.core.gemini._utils._convert_message_params._load_media",
    return_value=b"audio_data",
)
@patch(
    "mirascope.core.gemini._utils._convert_message_params.get_audio_type",
    return_value="unknown",
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
        match="Unsupported audio media type: audio/unknown. Gemini currently only supports WAV, MP3, AIFF, AAC, OGG, and FLAC audio file types.",
    ):
        convert_message_params([message])
    mock_load_media.assert_called_once_with("https://example.com/audio")
    mock_get_audio_type.assert_called_once_with(b"audio_data")


def test_audio_url_with_non_http() -> None:
    """Test audio_url part with a non-HTTP URL returns a FileData object."""
    message = BaseMessageParam(
        role="user",
        content=[AudioURLPart(type="audio_url", url="ftp://example.com/audio")],
    )
    result = convert_message_params([message])
    assert len(result) == 1
    part = result[0]["parts"][0]
    assert isinstance(part, protos.FileData)
    assert part.file_uri == "ftp://example.com/audio"


def test_tool_result_without_prior_parts() -> None:
    """Test tool_result part when there are no preceding parts."""
    message = BaseMessageParam(
        role="user",
        content=[
            ToolResultPart(type="tool_result", name="tool_only", content="only result")
        ],
    )
    result = convert_message_params([message])
    # Expect a single message with role "user" and a FunctionResponse part.
    assert result == [
        {
            "role": "user",
            "parts": [
                protos.FunctionResponse(
                    name="tool_only", response={"result": "only result"}
                )
            ],
        }
    ]


def test_string_content_non_user() -> None:
    """Test that a message with string content for a non-user role converts to model role."""
    message = BaseMessageParam(role="assistant", content="Hi there")
    result = convert_message_params([message])
    # For non-user roles, the role is set to "model"
    assert result == [{"role": "model", "parts": ["Hi there"]}]
