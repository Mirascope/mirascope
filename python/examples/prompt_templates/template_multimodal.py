from mirascope import llm


@llm.prompt_template("What book is this? {{ book_cover:image }}")
def image_prompt(book_cover: llm.Image | str | bytes): ...


@llm.prompt_template("Analyze this audio recording: {{ audio:audio }}")
def audio_prompt(audio: llm.Audio | str | bytes): ...


@llm.prompt_template("Summarize this video: {{ video:video }}")
def video_prompt(video: llm.Video | str | bytes): ...


@llm.prompt_template("Review this document: {{ doc:document }}")
def document_prompt(doc: llm.Document | str | bytes): ...


@llm.prompt_template("Compare these book covers: {{ covers:images }}")
def images_prompt(covers: list[llm.Image | str | bytes]): ...


@llm.prompt_template("Compare these audio clips: {{ clips:audios }}")
def audios_prompt(clips: list[llm.Audio | str | bytes]): ...


@llm.prompt_template("Do these video clips remind you of any book? {{ clips:videos }}")
def videos_prompt(clips: list[llm.Video | str | bytes]): ...


@llm.prompt_template("Review these documents: {{ docs:documents }}")
def documents_prompt(docs: list[llm.Document | str | bytes]): ...


@llm.prompt_template(
    """
    [USER]
    Analyze this multimedia presentation:
    - Cover image: {{ cover:image }}
    - Audio narration: {{ narration:audio }}
    - Supporting documents: {{ docs:documents }}
    
    What is the main theme?
    """
)
def mixed_media_prompt(
    cover: llm.Image | str | bytes,
    narration: llm.Audio | str | bytes,
    docs: list[llm.Document | str | bytes],
): ...
