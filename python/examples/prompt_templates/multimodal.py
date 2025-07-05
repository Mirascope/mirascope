from mirascope import llm


@llm.prompt("What book is this? {{ book_cover:image }}")
def image_prompt_template(book_cover: llm.Image | str | bytes): ...


@llm.prompt("Analyze this audio recording: {{ audio:audio }}")
def audio_prompt_template(audio: llm.Audio | str | bytes): ...


@llm.prompt("Review this document: {{ doc:document }}")
def document_prompt_template(doc: llm.Document | str | bytes): ...


@llm.prompt("Compare these book covers: {{ covers:images }}")
def images_prompt_template(covers: list[llm.Image | str | bytes]): ...


@llm.prompt("Compare these audio clips: {{ clips:audios }}")
def audios_prompt_template(clips: list[llm.Audio | str | bytes]): ...


@llm.prompt("Review these documents: {{ docs:documents }}")
def documents_prompt_template(docs: list[llm.Document | str | bytes]): ...


@llm.prompt(
    """
    Analyze this multimedia presentation:
    - Cover image: {{ cover:image }}
    - Audio narration: {{ narration:audio }}
    - Supporting documents: {{ docs:documents }}
    What is the main theme?
    """
)
def mixed_media_prompt_template(
    cover: llm.Image | str | bytes,
    narration: llm.Audio | str | bytes,
    docs: list[llm.Document | str | bytes],
): ...
