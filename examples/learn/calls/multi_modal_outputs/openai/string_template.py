import io
import wave

from pydub.playback import play

from mirascope.core import openai, prompt_template
from mirascope.core.openai import AudioSegment


@openai.call(
    "gpt-4o-audio-preview",
    call_params={
        "audio": {"voice": "alloy", "format": "wav"},
        "modalities": ["text", "audio"],
    },
)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


response = recommend_book(genre="fantasy")

print(response.audio_transcript)

audio_io = io.BytesIO(response.audio)

with wave.open(audio_io, "rb") as f:
    audio_segment = AudioSegment.from_raw(
        audio_io,
        sample_width=f.getsampwidth(),
        frame_rate=f.getframerate(),
        channels=f.getnchannels(),
    )

play(audio_segment)
