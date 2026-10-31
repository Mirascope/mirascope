"""MP3 frame detection through the public audio input APIs."""

import base64
from pathlib import Path

import pytest
from pytest_httpserver import HTTPServer

from mirascope import llm


def frame(second_byte: int, third_byte: int = 0x90) -> bytes:
    """Build a minimal frame header with enough data for MIME detection."""
    return bytes([0xFF, second_byte, third_byte]) + b"\x00" * 9


MP3_HEADERS = [
    pytest.param(frame(0xFA), id="mpeg1-crc"),
    pytest.param(frame(0xFB), id="mpeg1-no-crc"),
    pytest.param(frame(0xF2), id="mpeg2-crc"),
    pytest.param(frame(0xF3), id="mpeg2-no-crc"),
    pytest.param(frame(0xE2), id="mpeg2.5-crc"),
    pytest.param(frame(0xE3), id="mpeg2.5-no-crc"),
]


@pytest.mark.parametrize("data", MP3_HEADERS)
def test_from_bytes_recognizes_layer_three_and_preserves_payload(data: bytes) -> None:
    audio = llm.Audio.from_bytes(data)
    assert audio.source.mime_type == "audio/mp3"
    assert base64.b64decode(audio.source.data) == data


@pytest.mark.parametrize("data", MP3_HEADERS)
def test_from_file_recognizes_layer_three_without_an_mp3_extension(
    data: bytes, tmp_path: Path
) -> None:
    path = tmp_path / "audio.bin"
    path.write_bytes(data)
    audio = llm.Audio.from_file(str(path))
    assert audio.source.mime_type == "audio/mp3"
    assert base64.b64decode(audio.source.data) == data


@pytest.mark.parametrize("data", MP3_HEADERS)
def test_download_recognizes_layer_three(data: bytes, httpserver: HTTPServer) -> None:
    httpserver.expect_request("/audio").respond_with_data(data)
    audio = llm.Audio.download(httpserver.url_for("/audio"))
    assert audio.source.mime_type == "audio/mp3"
    assert base64.b64decode(audio.source.data) == data


@pytest.mark.asyncio
@pytest.mark.parametrize("data", MP3_HEADERS)
async def test_download_async_recognizes_layer_three(
    data: bytes, httpserver: HTTPServer
) -> None:
    httpserver.expect_request("/audio").respond_with_data(data)
    audio = await llm.Audio.download_async(httpserver.url_for("/audio"))
    assert audio.source.mime_type == "audio/mp3"
    assert base64.b64decode(audio.source.data) == data


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(b"\xfe\xf3\x90" + b"\x00" * 9, id="bad-first-sync-byte"),
        pytest.param(frame(0xD3), id="incomplete-frame-sync"),
        pytest.param(frame(0xEB), id="reserved-mpeg-version"),
        pytest.param(frame(0xE1), id="reserved-layer"),
        pytest.param(frame(0xF5), id="layer-two"),
        pytest.param(frame(0xF7), id="layer-one"),
        pytest.param(frame(0xFB, 0xF0), id="reserved-bitrate"),
        pytest.param(frame(0xFB, 0x9C), id="reserved-frequency"),
    ],
)
def test_non_mp3_and_invalid_headers_are_not_accepted_as_mp3(data: bytes) -> None:
    with pytest.raises(ValueError, match="Unsupported audio type"):
        llm.Audio.from_bytes(data)


@pytest.mark.parametrize("second_byte", [0xF1, 0xF9])
def test_aac_adts_is_not_misidentified_as_mp3(second_byte: int) -> None:
    audio = llm.Audio.from_bytes(frame(second_byte, 0x50))
    assert audio.source.mime_type == "audio/aac"


def test_mp3_free_bitrate_header_is_still_recognized() -> None:
    audio = llm.Audio.from_bytes(frame(0xF3, 0x00))
    assert audio.source.mime_type == "audio/mp3"
