from mirascope import llm


@llm.prompt_template()
def recommend_genre(genre: str) -> str:
    return f"Please recommend a {genre} book"


@llm.prompt_template()
def analyze_image(image: llm.Image) -> list[llm.Content]:
    return ["Please recommend a book, based on the themes in this image:", image]


@llm.prompt_template()  # No-op, as recommend_book_pirate is already a prompt template
def recommend_book_pirate(genre: str) -> llm.Prompt:
    return [
        llm.messages.system("You are a librarian, who always talks like a pirate"),
        llm.messages.user(f"I want to read a {genre} book!"),
    ]


@llm.prompt_template()
def recommend_genre_age_appropriate_prompt(genre: str, age: int) -> str:
    return f"""
    Please recommend a {genre} book that would be appropriate for a {age}-year-old reader.
    Include the title, author, and a brief description.
    Make sure the content is age-appropriate and engaging.
    """


@llm.prompt_template()
def pirate_prompt(genre: str) -> list[llm.Message]:
    return [
        llm.messages.system(
            "You are a conscientious librarian who talks like a pirate."
        ),
        llm.messages.user("Please recommend a book to me."),
        llm.messages.assistant("""
            Ahoy there, and greetings, matey!
            What manner of book be ye wanting?
            """),
        llm.messages.user(f"I'd like a {genre} book, please."),
    ]


@llm.prompt_template()
def image_prompt(book_cover: llm.Image) -> list[llm.Content]:
    return ["What book is this?", book_cover]


@llm.prompt_template()
def audio_prompt(audio: llm.Audio) -> list[llm.Content]:
    return ["Analyze this audio recording:", audio]


@llm.prompt_template()
def videos_prompt(clips: list[llm.Video]) -> list[llm.Content]:
    return ["Do these video clips remind you of any book?", *clips]


@llm.prompt_template()
def mixed_media_prompt(
    cover: llm.Image, narration: llm.Audio, docs: list[llm.Document]
) -> list[llm.Content]:
    return [
        """
        Analyze this multimedia presentation:
        - Cover image:
        """,
        cover,
        "- Audio narration:",
        narration,
        "- Supporting documents:",
        *docs,
        """
        
        What is the main theme?
        """,
    ]


@llm.prompt_template()
def history_prompt(history: list[llm.Message]) -> list[llm.Message]:
    return [
        llm.messages.system(
            "You are a summarization agent. Your job is to summarize long discussions."
        ),
        *history,
        llm.messages.user(
            "Please summarize our conversation, and recommend a book based on this chat."
        ),
    ]
