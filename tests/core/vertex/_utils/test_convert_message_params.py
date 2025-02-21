"""Tests the `vertex._utils.convert_message_params` function."""

import io
from unittest.mock import MagicMock, patch

import pytest
from vertexai.generative_models import Content, Part

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
from mirascope.core.vertex._utils._convert_message_params import convert_message_params


@patch("PIL.Image.open", new_callable=MagicMock)
def test_convert_message_params(mock_image_open: MagicMock) -> None:
    """Tests the `convert_message_params` function."""
    mock_image_open.return_value.format = "jpeg"
    message_params: list[BaseMessageParam | Content] = [
        BaseMessageParam(role="system", content="You are a helpful assistant."),
        BaseMessageParam(role="user", content="Hello"),
        Content(role="user", parts=[Part.from_text("Hello"), Part.from_text("Hello")]),
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
                TextPart(type="text", text="test"),
                ToolCallPart(type="tool_call", name="tool_name", args={"arg": "val"}),
                TextPart(type="text", text="test"),
            ],
        ),
    ]
    converted_message_params = convert_message_params(message_params)
    assert [p.to_dict() for p in converted_message_params] == [
        {"parts": [{"text": "You are a helpful assistant."}], "role": "system"},
        {"parts": [{"text": "Hello"}], "role": "user"},
        {"parts": [{"text": "Hello"}, {"text": "Hello"}], "role": "user"},
        {
            "parts": [
                {"text": "test"},
                {"inline_data": {"data": "aW1hZ2U=", "mime_type": "image/jpeg"}},
                {"inline_data": {"data": "YXVkaW8=", "mime_type": "audio/wav"}},
            ],
            "role": "user",
        },
        {
            "parts": [
                {
                    "function_response": {
                        "name": "tool_name",
                        "response": {"content": {"result": "result"}},
                    }
                }
            ],
            "role": "user",
        },
        {"parts": [{"text": "test"}], "role": "user"},
        {
            "parts": [{"function_call": {"args": {"arg": "val"}, "name": "tool_name"}}],
            "role": "user",
        },
        {"parts": [{"text": "test"}], "role": "user"},
    ]
    mock_image_open.assert_called_once()
    bytes_io: io.BytesIO = mock_image_open.call_args.args[0]
    assert bytes_io.getvalue() == b"image"

    with pytest.raises(
        ValueError,
        match="Unsupported image media type: image/svg. Vertex currently only supports "
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
        match="Failed to load or encode data from http://example.com/image",
    ):
        convert_message_params(
            [
                BaseMessageParam(
                    role="user",
                    content=[
                        ImageURLPart(
                            type="image_url",
                            url="http://example.com/image",
                            detail=None,
                        )
                    ],
                ),
            ]
        )

    with pytest.raises(
        ValueError,
        match="Unsupported audio media type: audio/unknown. "
        "Vertex currently only supports WAV, MP3, AIFF, AAC, OGG, "
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
            ]
        )

    with pytest.raises(
        ValueError,
        match="Vertex currently only supports text, image, and audio parts. Part provided: cache_control",
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


@patch(
    "mirascope.core.vertex._utils._convert_message_params._load_media",
    return_value=b"imagedata",
)
@patch("PIL.Image.open", new_callable=MagicMock)
@patch("mirascope.core.vertex._utils._convert_message_params.Part.from_uri")
def test_image_url_conversion(
    mock_from_uri, mock_image_open: MagicMock, mock_load_media
) -> None:
    """Tests conversion of an image_url part."""
    # Patch PIL.Image.MIME so that the lookup for "JPEG" succeeds.
    with patch.dict("PIL.Image.MIME", {"JPEG": "image/jpeg"}):
        dummy_image = MagicMock()
        dummy_image.format = "JPEG"
        mock_image_open.return_value = dummy_image

        # Define a dummy Part to be returned by Part.from_uri.
        class DummyPart:
            def __init__(self, data):
                # Set _raw_part to mimic a valid Part with file_data.
                self._raw_part = {
                    "file_data": {
                        "file_uri": data["file_uri"],
                        "mime_type": data["mime_type"],
                    }
                }

            def to_dict(self):
                return self._raw_part

        expected_dummy = DummyPart(
            {"file_uri": "http://example.com/image", "mime_type": "image/jpeg"}
        )
        mock_from_uri.return_value = expected_dummy

        # Create an instance of ImageURLPart.
        dummy_part = ImageURLPart(
            type="image_url", url="http://example.com/image", detail="auto"
        )
        message = BaseMessageParam(role="user", content=[dummy_part])
        result = convert_message_params([message])
        result_dicts = [p.to_dict() for p in result]
        expected = {"role": "user", "parts": [expected_dummy.to_dict()]}
        assert result_dicts == [expected]
        mock_load_media.assert_called_once_with("http://example.com/image")
        mock_from_uri.assert_called_once_with(
            "http://example.com/image", mime_type="image/jpeg"
        )


@patch(
    "mirascope.core.vertex._utils._convert_message_params._load_media",
    return_value=b"imagedata",
)
@patch("PIL.Image.open", new_callable=MagicMock)
@patch("mirascope.core.vertex._utils._convert_message_params.Part.from_uri")
def test_image_url_conversion_with_format_invalid(
    mock_from_uri, mock_image_open: MagicMock, mock_load_media
) -> None:
    """Tests conversion of an image_url part with format invalid."""
    with patch.dict("PIL.Image.MIME", {"JPEG": "image/invalid"}):
        dummy_image = MagicMock()
        dummy_image.format = "JPEG"
        mock_image_open.return_value = dummy_image

        # Define a dummy Part to be returned by Part.from_uri.
        class DummyPart:
            def __init__(self, data):
                # Set _raw_part to mimic a valid Part with file_data.
                self._raw_part = {
                    "file_data": {
                        "file_uri": data["file_uri"],
                        "mime_type": data["mime_type"],
                    }
                }

            def to_dict(self): ...

        expected_dummy = DummyPart(
            {"file_uri": "http://example.com/image", "mime_type": "image/jpeg"}
        )
        mock_from_uri.return_value = expected_dummy

        # Create an instance of ImageURLPart.
        dummy_part = ImageURLPart(
            type="image_url", url="http://example.com/image", detail="auto"
        )
        message = BaseMessageParam(role="user", content=[dummy_part])
        with pytest.raises(
            ValueError,
            match="Unsupported image media type: image/invalid. Gemini currently only supports JPEG, PNG, WebP, HEIC, and HEIF images.",
        ):
            convert_message_params([message])


@patch(
    "mirascope.core.vertex._utils._convert_message_params._load_media",
    return_value=b"audiodata",
)
@patch(
    "mirascope.core.vertex._utils._convert_message_params.get_audio_type",
    return_value="mp3",
)
@patch("mirascope.core.vertex._utils._convert_message_params.Part.from_uri")
def test_audio_url_conversion_valid(
    mock_from_uri, mock_get_audio_type, mock_load_media
) -> None:
    """Tests conversion of a valid audio_url part."""

    class DummyPart:
        def __init__(self, data):
            # Mimic a valid Part with file_data.
            self._raw_part = {
                "file_data": {
                    "file_uri": data["file_uri"],
                    "mime_type": data["mime_type"],
                }
            }

        def to_dict(self):
            return self._raw_part

    expected_dummy = DummyPart(
        {"file_uri": "http://example.com/audio", "mime_type": "audio/mp3"}
    )
    mock_from_uri.return_value = expected_dummy

    # Create an instance of AudioURLPart.
    dummy_part = AudioURLPart(type="audio_url", url="http://example.com/audio")
    message = BaseMessageParam(role="user", content=[dummy_part])
    result = convert_message_params([message])
    result_dicts = [p.to_dict() for p in result]
    expected = {"role": "user", "parts": [expected_dummy.to_dict()]}
    assert result_dicts == [expected]
    mock_load_media.assert_called_once_with("http://example.com/audio")
    mock_get_audio_type.assert_called_once_with(b"audiodata")
    mock_from_uri.assert_called_once_with(
        "http://example.com/audio", mime_type="audio/mp3"
    )


@patch(
    "mirascope.core.vertex._utils._convert_message_params._load_media",
    return_value=b"audiodata",
)
@patch(
    "mirascope.core.vertex._utils._convert_message_params.get_audio_type",
    return_value="invalid",
)
def test_audio_url_conversion_invalid(mock_get_audio_type, mock_load_media) -> None:
    """Tests conversion of an audio_url part with an unsupported audio type."""
    dummy_part = AudioURLPart(type="audio_url", url="http://example.com/audio")
    message = BaseMessageParam(role="user", content=[dummy_part])
    with pytest.raises(
        ValueError,
        match=r"Unsupported audio media type: audio/invalid\. Gemini currently only supports WAV, MP3, AIFF, AAC, OGG, and FLAC audio file types\.",
    ):
        convert_message_params([message])
    mock_load_media.assert_called_once_with("http://example.com/audio")
    mock_get_audio_type.assert_called_once_with(b"audiodata")
