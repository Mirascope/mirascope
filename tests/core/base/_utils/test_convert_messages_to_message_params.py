import io
import wave
from unittest.mock import MagicMock, Mock, patch

import pytest

from mirascope.core import BaseMessageParam
from mirascope.core.base import AudioPart, DocumentPart, ImagePart, TextPart
from mirascope.core.base._utils._convert_messages_to_message_params import (
    _convert_message_sequence_part_to_content_part,
    _is_base_message_params,
    convert_message_content_to_message_param_content,
    convert_messages_to_message_params,
)


class MockAudioSegment:
    def set_frame_rate(self, frame_rate):
        return self

    def set_channels(self, channels):
        return self

    def set_sample_width(self, sample_width):
        return self

    def export(self, format):
        return io.BytesIO(b"mock_wav_data")


def test_convert_message_sequence_part_to_content_part_with_string():
    input_value = "Hello, World!"
    expected_output = TextPart(text="Hello, World!", type="text")
    result = _convert_message_sequence_part_to_content_part(input_value)
    assert result == expected_output


def test_convert_message_sequence_part_to_content_part_with_text_part():
    input_value = TextPart(type="text", text="Hello, World!")
    result = _convert_message_sequence_part_to_content_part(input_value)
    assert result == input_value


def test_convert_message_sequence_part_to_content_part_with_image_part():
    input_value = ImagePart(
        type="image",
        media_type="image/png",
        image=b"image_bytes",
        detail=None,
    )
    result = _convert_message_sequence_part_to_content_part(input_value)
    assert result == input_value


def test_convert_message_sequence_part_to_content_part_with_audio_part():
    input_value = AudioPart(
        type="audio",
        media_type="audio/wav",
        audio=b"audio_bytes",
    )
    result = _convert_message_sequence_part_to_content_part(input_value)
    assert result == input_value


def test_convert_message_sequence_part_to_content_part_with_document_part():
    input_value = DocumentPart(
        type="document",
        media_type="application/pdf",
        document=b"document_bytes",
    )
    result = _convert_message_sequence_part_to_content_part(input_value)
    assert result == input_value


@patch(
    "mirascope.core.base._utils._convert_messages_to_message_params.pil_image_to_bytes",
    new_callable=MagicMock,
)
def test_convert_message_sequence_part_to_content_part_with_pil_image(
    mock_pil_image_to_bytes: MagicMock,
):
    mock_pil_image_to_bytes.return_value = b"image_bytes"
    mock_image_instance = Mock()
    mock_image_instance.format = "PNG"

    from PIL import Image

    with (
        patch(
            "mirascope.core.base._utils._convert_messages_to_message_params.has_pil_module",
            True,
        ),
        patch(
            "mirascope.core.base._utils._convert_messages_to_message_params.Image.Image",
            Mock,
        ),
        patch(
            "mirascope.core.base._utils._convert_messages_to_message_params.isinstance",
            side_effect=lambda obj, cls: True
            if cls == Image.Image
            else isinstance(obj, cls),
        ),
    ):
        result = _convert_message_sequence_part_to_content_part(mock_image_instance)
        expected_output = ImagePart(
            type="image",
            media_type="image/png",
            image=b"image_bytes",
            detail=None,
        )
        assert result == expected_output


def test_convert_message_sequence_part_to_content_part_invalid_type():
    input_value = 12345
    with pytest.raises(ValueError) as exc_info:
        _convert_message_sequence_part_to_content_part(input_value)  # pyright: ignore [reportArgumentType]
    assert f"Invalid message sequence type: {input_value}" in str(exc_info.value)


def test_convert_message_sequence_to_content():
    input_sequence = [
        "Hello",
        TextPart(type="text", text="World"),
        ImagePart(
            type="image",
            media_type="image/jpeg",
            image=b"image_bytes",
            detail=None,
        ),
        AudioPart(
            type="audio",
            media_type="audio/mp3",
            audio=b"audio_bytes",
        ),
    ]
    expected_output = [
        TextPart(type="text", text="Hello"),
        TextPart(type="text", text="World"),
        ImagePart(
            type="image",
            media_type="image/jpeg",
            image=b"image_bytes",
            detail=None,
        ),
        AudioPart(
            type="audio",
            media_type="audio/mp3",
            audio=b"audio_bytes",
        ),
    ]
    result = convert_message_content_to_message_param_content(input_sequence)
    assert result == expected_output


def test_is_base_message_params_with_base_message_param_list():
    input_value = [
        BaseMessageParam(role="user", content="Hello"),
        BaseMessageParam(role="assistant", content="Hi there!"),
    ]
    result = _is_base_message_params(input_value)
    assert result is True


def test_is_base_message_params_with_invalid_list():
    input_value = ["Hello", "World"]
    result = _is_base_message_params(input_value)
    assert result is False


def test_convert_messages_to_message_params_with_string():
    messages = "Hello, World!"
    result = convert_messages_to_message_params(messages)
    expected_output = [BaseMessageParam(role="user", content="Hello, World!")]
    assert result == expected_output


def test_convert_messages_to_message_params_with_base_message_param():
    message_param = BaseMessageParam(role="user", content="Hello")
    result = convert_messages_to_message_params(message_param)
    assert result == [message_param]


def test_convert_messages_to_message_params_with_sequence():
    messages = ["Hello", "World"]

    expected_output = [
        BaseMessageParam(
            role="user",
            content=[
                TextPart(type="text", text="Hello"),
                TextPart(type="text", text="World"),
            ],
        )
    ]
    result = convert_messages_to_message_params(messages)
    assert result == expected_output


def test_convert_messages_to_message_params_with_invalid_type():
    messages = 12345
    with pytest.raises(ValueError) as exc_info:
        convert_messages_to_message_params(messages)  # pyright: ignore [reportArgumentType]
    assert f"Invalid messages type: {messages}" in str(exc_info.value)


def test_convert_messages_to_message_params_with_custom_role():
    messages = "Hello, World!"
    result = convert_messages_to_message_params(messages, role="custom_role")
    expected_output = [BaseMessageParam(role="custom_role", content="Hello, World!")]
    assert result == expected_output


def test_convert_message_sequence_part_to_content_part_with_audio_segment():
    mock_audio_segment = MockAudioSegment()

    with (
        patch(
            "mirascope.core.base._utils._convert_messages_to_message_params.has_pydub_module",
            True,
        ),
        patch(
            "mirascope.core.base._utils._convert_messages_to_message_params.AudioSegment",
            MockAudioSegment,
        ),
    ):
        result = _convert_message_sequence_part_to_content_part(mock_audio_segment)  # pyright: ignore [reportArgumentType]

    expected_output = AudioPart(
        type="audio",
        media_type="audio/wav",
        audio=b"mock_wav_data",
    )
    assert result == expected_output


def test_convert_message_sequence_part_to_content_part_with_wave_read():
    wav_data = io.BytesIO()
    with wave.open(wav_data, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(44100)
        wav_file.writeframes(b"\x00\x00" * 1000)  # 1000 samples of silence

    wav_data.seek(0)
    with wave.open(wav_data, "rb") as wave_read:
        result = _convert_message_sequence_part_to_content_part(wave_read)

        expected_output = AudioPart(
            type="audio",
            media_type="audio/wav",
            audio=b"\x00\x00" * 1000,
        )
        assert result == expected_output
