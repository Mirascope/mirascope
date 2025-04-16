"""Tests the `google._utils.convert_message_params` function."""

import io
from unittest.mock import AsyncMock, MagicMock, patch

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
    ToolCallPart,
    ToolResultPart,
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
        match="Google currently only supports text, tool_call, tool_result, image, and audio parts. Part provided: cache_control",
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


def test_image_url_with_http_valid() -> None:
    """Test image_url part with an HTTP URL and valid media type."""
    message = BaseMessageParam(
        role="user",
        content=[
            ImageURLPart(type="image_url", url="https://example.com/image", detail=None)
        ],
    )
    result = convert_message_params([message], MagicMock())
    assert result == [
        {
            "parts": [
                {
                    "file_data": {
                        "file_uri": "https://example.com/image",
                        "mime_type": None,
                    }
                }
            ],
            "role": "user",
        }
    ]


@patch(
    "mirascope.core.google._utils._convert_message_params._load_media",
    return_value=b"image_url_data",
)
@patch(
    "mirascope.core.google._utils._convert_message_params.get_image_type",
    return_value="png",
)
def test_image_url_with_http_valid_gemini(
    mock_get_image_type: MagicMock, mock_load_media: MagicMock
) -> None:
    """Test image_url part with an HTTP URL and valid media type."""
    message = BaseMessageParam(
        role="user",
        content=[
            ImageURLPart(type="image_url", url="https://example.com/image", detail=None)
        ],
    )
    mock_client = MagicMock()
    mock_client.vertexai = False
    mock_file = MagicMock(uri="file://local/path/image", mime_type="image/png")
    mock_client.files.upload.return_value = mock_file
    result = convert_message_params([message], mock_client)
    assert result == [
        {
            "parts": [
                {
                    "inline_data": {
                        "data": b"image_url_data",
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
@patch(
    "mirascope.core.google._utils._convert_message_params.get_image_type",
    return_value="svg",
)
def test_image_url_with_http_invalid_media_type(
    mock_get_image_type: MagicMock, mock_load_media: MagicMock
) -> None:
    """Test image_url part with an HTTP URL and an invalid media type raises ValueError."""
    message = BaseMessageParam(
        role="user",
        content=[
            ImageURLPart(type="image_url", url="https://example.com/image", detail=None)
        ],
    )
    with pytest.raises(
        ValueError,
        match="Unsupported image media type: image/svg. Google currently only supports JPEG, PNG, WebP, HEIC, and HEIF images.",
    ):
        client = MagicMock()
        client.vertexai = False
        convert_message_params([message], client)


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


def test_audio_url_with_http_valid() -> None:
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
                        "mime_type": None,
                    }
                },
            ],
            "role": "user",
        }
    ]


@patch(
    "mirascope.core.google._utils._convert_message_params.get_audio_type",
    return_value="wav",
)
@patch(
    "mirascope.core.google._utils._convert_message_params._load_media",
    return_value=b"audio_data",
)
def test_audio_url_with_http_valid_gemini(
    mock_load_media: MagicMock, mock_get_audio_type: MagicMock
) -> None:
    """Test image_url part with an HTTP URL and valid media type."""
    message = BaseMessageParam(
        role="user",
        content=[AudioURLPart(type="audio_url", url="https://example.com/audio")],
    )
    mock_client = MagicMock()
    mock_client.vertexai = False
    mock_file = MagicMock(uri="file://local/path/audio", mime_type="audio/wav")
    mock_client.files.upload.return_value = mock_file
    result = convert_message_params([message], mock_client)
    assert result == [
        {
            "parts": [
                {
                    "inline_data": {
                        "data": b"audio_data",
                        "mime_type": "audio/wav",
                    }
                }
            ],
            "role": "user",
        }
    ]
    mock_load_media.assert_called_once_with("https://example.com/audio")


@patch(
    "mirascope.core.google._utils._convert_message_params._load_media",
    return_value=b"audio_data",
)
@patch(
    "mirascope.core.google._utils._convert_message_params.get_audio_type",
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
        match="Unsupported audio media type: audio/unknown. Google currently only supports WAV, MP3, AIFF, AAC, OGG, and FLAC audio file types.",
    ):
        client = MagicMock()
        client.vertexai = False
        convert_message_params([message], client)
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


def test_async_large_image_upload() -> None:
    """Test async upload of large images (>15MB)."""
    # Create a large image (>15MB)
    large_image = bytes([0] * (22 * 1024 * 1024))  # 22MB

    message = BaseMessageParam(
        role="user",
        content=[
            ImagePart(
                type="image", media_type="image/jpeg", image=large_image, detail=None
            )
        ],
    )

    mock_client = MagicMock()
    mock_client.vertexai = False
    mock_client.aio = MagicMock()
    mock_client.aio.files = MagicMock()
    mock_file = MagicMock(uri="file://uploaded/image", mime_type="image/jpeg")
    mock_client.aio.files.upload = AsyncMock(return_value=mock_file)

    result = convert_message_params([message], mock_client)

    assert result == [
        {
            "parts": [
                {
                    "file_data": {
                        "file_uri": "file://uploaded/image",
                        "mime_type": "image/jpeg",
                    }
                }
            ],
            "role": "user",
        }
    ]

    # Verify async upload was called
    mock_client.aio.files.upload.assert_called_once()
    call_args = mock_client.aio.files.upload.call_args
    assert isinstance(call_args[1]["file"], io.BytesIO)
    assert call_args[1]["config"]["mime_type"] == "image/jpeg"


@patch(
    "mirascope.core.google._utils._convert_message_params._load_media",
    return_value=bytes([0] * (22 * 1024 * 1024)),
)
@patch(
    "mirascope.core.google._utils._convert_message_params.get_image_type",
    return_value="jpeg",
)
def test_large_image_url_upload(
    mock_get_image_type: MagicMock, mock_load_media: MagicMock
) -> None:
    """Test large image URL upload."""
    message = BaseMessageParam(
        role="user",
        content=[
            ImageURLPart(type="image_url", url="https://example.com/large", detail=None)
        ],
    )
    mock_client = MagicMock()
    mock_client.vertexai = False
    mock_client.aio = MagicMock()
    mock_client.aio.files = MagicMock()
    mock_file = MagicMock(uri="file://uploaded/image", mime_type="image/jpeg")
    mock_client.aio.files.upload = AsyncMock(return_value=mock_file)

    result = convert_message_params([message], mock_client)

    assert result == [
        {
            "parts": [
                {
                    "file_data": {
                        "file_uri": "file://uploaded/image",
                        "mime_type": "image/jpeg",
                    }
                }
            ],
            "role": "user",
        }
    ]

    # Verify async upload was called
    mock_client.aio.files.upload.assert_called_once()
    call_args = mock_client.aio.files.upload.call_args
    assert isinstance(call_args[1]["file"], io.BytesIO)
    assert call_args[1]["config"]["mime_type"] == "image/jpeg"


@patch(
    "mirascope.core.google._utils._convert_message_params._load_media",
    return_value=bytes([0] * (22 * 1024 * 1024)),
)
@patch(
    "mirascope.core.google._utils._convert_message_params.get_audio_type",
    return_value="wav",
)
def test_large_audio_url_upload(
    mock_get_audio_type: MagicMock, mock_load_media: MagicMock
) -> None:
    """Test large audio URL upload."""
    message = BaseMessageParam(
        role="user",
        content=[AudioURLPart(type="audio_url", url="https://example.com/large")],
    )
    mock_client = MagicMock()
    mock_client.vertexai = False
    mock_client.aio = MagicMock()
    mock_client.aio.files = MagicMock()
    mock_file = MagicMock(uri="file://uploaded/audio", mime_type="audio/wav")
    mock_client.aio.files.upload = AsyncMock(return_value=mock_file)

    result = convert_message_params([message], mock_client)

    assert result == [
        {
            "parts": [
                {
                    "file_data": {
                        "file_uri": "file://uploaded/audio",
                        "mime_type": "audio/wav",
                    }
                }
            ],
            "role": "user",
        }
    ]

    # Verify async upload was called
    mock_client.aio.files.upload.assert_called_once()
    call_args = mock_client.aio.files.upload.call_args
    assert isinstance(call_args[1]["file"], io.BytesIO)
    assert call_args[1]["config"]["mime_type"] == "audio/wav"


def test_multiple_async_image_uploads() -> None:
    """Test multiple concurrent async image uploads."""
    large_image = bytes([0] * (16 * 1024 * 1024))  # 16MB

    message = BaseMessageParam(
        role="user",
        content=[
            ImagePart(
                type="image", media_type="image/jpeg", image=large_image, detail=None
            ),
            TextPart(type="text", text="Some text in between"),
            ImagePart(
                type="image", media_type="image/png", image=large_image, detail=None
            ),
        ],
    )

    mock_client = MagicMock()
    mock_client.vertexai = False
    mock_client.aio = MagicMock()
    mock_client.aio.files = MagicMock()

    mock_files = [
        MagicMock(uri=f"file://uploaded/image{i}", mime_type=f"image/{fmt}")
        for i, fmt in enumerate(["jpeg", "png"])
    ]
    mock_client.aio.files.upload = AsyncMock(side_effect=mock_files)

    result = convert_message_params([message], mock_client)

    assert result == [
        {
            "parts": [
                {
                    "file_data": {
                        "file_uri": "file://uploaded/image0",
                        "mime_type": "image/jpeg",
                    }
                },
                {"text": "Some text in between"},
                {
                    "file_data": {
                        "file_uri": "file://uploaded/image1",
                        "mime_type": "image/png",
                    }
                },
            ],
            "role": "user",
        }
    ]

    assert mock_client.aio.files.upload.call_count == 2
    calls = mock_client.aio.files.upload.call_args_list
    assert calls[0][1]["config"]["mime_type"] == "image/jpeg"
    assert calls[1][1]["config"]["mime_type"] == "image/png"


def test_async_upload_error_handling() -> None:
    """Test error handling during async uploads."""
    large_image = bytes([0] * (16 * 1024 * 1024))  # 16MB

    message = BaseMessageParam(
        role="user",
        content=[
            ImagePart(
                type="image", media_type="image/jpeg", image=large_image, detail=None
            ),
        ],
    )

    mock_client = MagicMock()
    mock_client.vertexai = False
    mock_client.aio = MagicMock()
    mock_client.aio.files = MagicMock()
    mock_client.aio.files.upload = AsyncMock(side_effect=Exception("Upload failed"))

    with pytest.raises(Exception) as exc_info:
        convert_message_params([message], mock_client)
    assert str(exc_info.value) == "Upload failed"


def test_mixed_content_with_async_uploads() -> None:
    """Test handling mixed content types with some requiring async uploads. And also testing that only images
    actually put in the message are counted towards the 15MB limit."""
    large_image = bytes([0] * (16 * 1024 * 1024))  # 16MB
    small_image = bytes([0] * (1 * 1024 * 1024))  # 1MB

    message = BaseMessageParam(
        role="user",
        content=[
            TextPart(type="text", text="Start text"),
            ImagePart(
                type="image", media_type="image/jpeg", image=large_image, detail=None
            ),
            ImagePart(
                type="image", media_type="image/png", image=small_image, detail=None
            ),
            TextPart(type="text", text="End text"),
        ],
    )

    mock_client = MagicMock()
    mock_client.vertexai = False
    mock_client.aio = MagicMock()
    mock_client.aio.files = MagicMock()
    mock_file = MagicMock(uri="file://uploaded/large_image", mime_type="image/jpeg")
    mock_client.aio.files.upload = AsyncMock(return_value=mock_file)

    result = convert_message_params([message], mock_client)

    assert result == [
        {
            "parts": [
                {"text": "Start text"},
                {
                    "file_data": {
                        "file_uri": "file://uploaded/large_image",
                        "mime_type": "image/jpeg",
                    }
                },
                {
                    "inline_data": {
                        "data": small_image,
                        "mime_type": "image/png",
                    }
                },
                {"text": "End text"},
            ],
            "role": "user",
        }
    ]

    # Verify only large image was uploaded async
    mock_client.aio.files.upload.assert_called_once()
    call_args = mock_client.aio.files.upload.call_args
    assert call_args[1]["config"]["mime_type"] == "image/jpeg"


def test_audio_part_handling() -> None:
    """Test handling of audio parts including large and small audio files."""
    large_audio = bytes([0] * (16 * 1024 * 1024))  # 16MB
    small_audio = bytes([0] * (1 * 1024 * 1024))  # 1MB

    message = BaseMessageParam(
        role="user",
        content=[
            TextPart(type="text", text="Start text"),
            AudioPart(type="audio", media_type="audio/wav", audio=large_audio),
            AudioPart(type="audio", media_type="audio/mp3", audio=small_audio),
            TextPart(type="text", text="End text"),
        ],
    )

    mock_client = MagicMock()
    mock_client.vertexai = False
    mock_client.aio = MagicMock()
    mock_client.aio.files = MagicMock()
    mock_file = MagicMock(uri="file://uploaded/large_audio", mime_type="audio/wav")
    mock_client.aio.files.upload = AsyncMock(return_value=mock_file)

    result = convert_message_params([message], mock_client)

    assert result == [
        {
            "parts": [
                {"text": "Start text"},
                {
                    "file_data": {
                        "file_uri": "file://uploaded/large_audio",
                        "mime_type": "audio/wav",
                    }
                },
                {
                    "inline_data": {
                        "data": small_audio,
                        "mime_type": "audio/mp3",
                    }
                },
                {"text": "End text"},
            ],
            "role": "user",
        }
    ]

    # Verify only large audio was uploaded async
    mock_client.aio.files.upload.assert_called_once()
    call_args = mock_client.aio.files.upload.call_args
    assert call_args[1]["config"]["mime_type"] == "audio/wav"


@pytest.mark.asyncio
async def test_convert_message_in_running_loop():
    """Tests convert_message_params in an async context."""
    result = convert_message_params([], MagicMock())
    assert result == []


def test_tool_call_parts() -> None:
    """Test handling of tool_call parts."""
    message = BaseMessageParam(
        role="user",
        content=[
            TextPart(type="text", text="I need to search for something"),
            ToolCallPart(
                type="tool_call",
                name="search",
                args={"query": "python programming"},
                id="tool-1234",
            ),
        ],
    )

    result = convert_message_params([message], MagicMock())

    assert result == [
        {
            "parts": [
                {"text": "I need to search for something"},
                {
                    "function_call": {
                        "name": "search",
                        "args": {"query": "python programming"},
                        "id": "tool-1234",
                    }
                },
            ],
            "role": "user",
        }
    ]


def test_tool_result_parts() -> None:
    """Test handling of tool_result parts."""
    message = BaseMessageParam(
        role="assistant",
        content=[
            TextPart(type="text", text="Here are the search results:"),
            ToolResultPart(
                type="tool_result",
                name="search",
                content="Python is a programming language",
                id="tool-1234",
            ),
        ],
    )

    result = convert_message_params([message], MagicMock())

    assert result == [
        {
            "parts": [
                {"text": "Here are the search results:"},
                {
                    "function_response": {
                        "name": "search",
                        "response": {
                            "content": "Python is a programming language",
                        },
                        "id": "tool-1234",
                    }
                },
            ],
            "role": "model",
        }
    ]
