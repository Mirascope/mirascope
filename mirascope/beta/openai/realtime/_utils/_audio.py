import asyncio
import base64
import io
from io import BytesIO
from typing import Any

from pydub import AudioSegment

SAMPLE_WIDTH = 2
FRAME_RATE = 24000
CHANNELS = 1


def audio_chunk_to_audio_segment(audio_bytes: bytes) -> AudioSegment:
    return AudioSegment.from_raw(
        io.BytesIO(audio_bytes),
        sample_width=SAMPLE_WIDTH,
        frame_rate=FRAME_RATE,
        channels=CHANNELS,
    )


def _encode_pcm_as_base64(audio_bytes: bytes | BytesIO) -> str:
    # Load the audio file from the byte stream
    audio = AudioSegment.from_file(
        io.BytesIO(audio_bytes) if isinstance(audio_bytes, bytes) else audio_bytes
    )

    # Resample to 24kHz mono pcm16
    pcm_audio = (
        audio.set_frame_rate(FRAME_RATE)
        .set_channels(CHANNELS)
        .set_sample_width(SAMPLE_WIDTH)
        .raw_data
    )

    # Encode to base64 string
    return base64.b64encode(pcm_audio).decode()


def audio_to_input_audio_buffer_append_event(
    audio_bytes: bytes | BytesIO,
) -> dict[str, Any]:
    return {
        "type": "input_audio_buffer.append",
        "audio": _encode_pcm_as_base64(audio_bytes),
    }


async def async_audio_input_audio_buffer_append_event(
    audio_bytes: bytes | BytesIO,
) -> dict[str, Any]:
    return await asyncio.to_thread(
        audio_to_input_audio_buffer_append_event, audio_bytes
    )


def audio_to_item_create_event(audio_bytes: bytes | BytesIO) -> dict[str, Any]:
    return {
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "user",
            "content": [
                {"type": "input_audio", "audio": _encode_pcm_as_base64(audio_bytes)}
            ],
        },
    }


async def async_audio_to_item_create_event(
    audio_bytes: bytes | BytesIO,
) -> dict[str, Any]:
    return await asyncio.to_thread(audio_to_item_create_event, audio_bytes)
