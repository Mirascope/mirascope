from mirascope import llm

text_msg = llm.user("Hello, how are you?")

image = llm.Image(
    data="/path/to/book-cover.jpg",  # or URL, base64, or bytes
    mime_type="image/jpeg",
)
image_msg = llm.user(["What book is shown in this image?", image])

audio = llm.Audio(
    data="/path/to/audio-question.mp3",  # or URL, base64, or bytes
    mime_type="audio/mp3",
    transcript="What's your favorite book genre?",  # optional
)
audio_msg = llm.user(audio)

mixed_msg = llm.user(
    [
        "I have a question about this book cover:",
        image,
        "Can you tell me what genre this appears to be?",
    ]
)
