"""Tests the `_utils.get_audio_type` module."""

import pytest

from mirascope.core.base._utils._get_audio_type import get_audio_type

WAV_DATA = b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"

MP3_DATA = b"ID3\x03\x00\x00\x00\x00\x00\x1f"

AIFF_DATA = b"FORM\x00\x00\x00\x00AIFFCOMM"

AAC_DATA = b"\xff\xf1"

OGG_DATA = b"OggS\x00\x02"

FLAC_DATA = b"fLaC\x00\x00\x00\x22\x10\x00\x00\x00\x01"


def test_get_audio_type() -> None:
    """Test the get_audio_type function."""
    assert get_audio_type(WAV_DATA) == "wav"
    assert get_audio_type(MP3_DATA) == "mp3"
    assert get_audio_type(AIFF_DATA) == "aiff"
    assert get_audio_type(AAC_DATA) == "aac"
    assert get_audio_type(OGG_DATA) == "ogg"
    assert get_audio_type(FLAC_DATA) == "flac"
    with pytest.raises(ValueError, match="Unsupported audio type"):
        get_audio_type(b"invalid")
