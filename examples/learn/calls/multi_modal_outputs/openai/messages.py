import io
import wave

from pydub.playback import play
from pydub import AudioSegment

from mirascope.core import openai, Messages


@openai.call(
    "gpt-4o-audio-preview",
    call_params={
        "audio": {"voice": "alloy", "format": "wav"},
        "modalities": ["text", "audio"],
    },
)
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


response = recommend_book(genre="fantasy")

print(response.audio_transcript)

if audio := response.audio:
    audio_io = io.BytesIO(audio)

    with wave.open(audio_io, "rb") as f:
        audio_segment = AudioSegment.from_raw(audio_io)

    play(audio_segment)
