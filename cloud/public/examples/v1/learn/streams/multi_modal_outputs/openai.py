import io


from pydub.playback import play
from pydub import AudioSegment

from mirascope.core import openai, Messages

SAMPLE_WIDTH = 2
FRAME_RATE = 24000
CHANNELS = 1


@openai.call(
    "gpt-4o-audio-preview",
    call_params={
        "audio": {"voice": "alloy", "format": "pcm16"}, # [!code highlight]
        "modalities": ["text", "audio"], # [!code highlight]
    },
    stream=True, # [!code highlight]
)
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


audio_chunk = b""
audio_transcript_chunk = ""

stream = recommend_book("fantasy")
for chunk, _ in stream:
    if chunk.audio: # [!code highlight]
        audio_chunk += chunk.audio # [!code highlight]
    if chunk.audio_transcript: # [!code highlight]
        audio_transcript_chunk += chunk.audio_transcript # [!code highlight]

print(audio_transcript_chunk)


audio_segment = AudioSegment.from_raw(
    io.BytesIO(audio_chunk),
    sample_width=SAMPLE_WIDTH,
    frame_rate=FRAME_RATE,
    channels=CHANNELS,
)
play(audio_segment)
