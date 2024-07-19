"""Utility for determining the type of an audio file from its bytes."""


def get_audio_type(audio_data: bytes) -> str:
    if audio_data.startswith(b"RIFF") and audio_data[8:12] == b"WAVE":
        return "wav"
    elif audio_data.startswith(b"ID3") or audio_data.startswith(b"\xff\xfb"):
        return "mp3"
    elif audio_data.startswith(b"FORM") and audio_data[8:12] == b"AIFF":
        return "aiff"
    elif audio_data.startswith(b"\xff\xf1") or audio_data.startswith(b"\xff\xf9"):
        return "aac"
    elif audio_data.startswith(b"OggS"):
        return "ogg"
    elif audio_data.startswith(b"fLaC"):
        return "flac"

    raise ValueError("Unsupported audio type")
