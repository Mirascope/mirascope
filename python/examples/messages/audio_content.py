from mirascope import llm

# Audio from local file
audio = llm.Audio.from_file("recording.mp3")

# Audio from raw bytes
audio_bytes = llm.Audio.from_bytes(b"...")

# Include audio in a message
message = llm.messages.user(["Please transcribe this audio:", audio])
