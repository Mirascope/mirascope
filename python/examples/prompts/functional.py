import inspect

from mirascope import llm


@llm.prompt()
def simple_prompt() -> str:
    return "Please recommend a book"


@llm.prompt()
def genre_prompt(genre: str) -> str:
    return f"Please recommend a {genre} book"


@llm.prompt()
def detailed_prompt(genre: str, age: int) -> str:
    return inspect.cleandoc(
        f"""
        Please recommend a {genre} book that would be appropriate for a {age}-year-old reader.
        Include the title, author, and a brief description.
        Make sure the content is age-appropriate and engaging.
        """
    )


@llm.prompt()
def pirate_prompt(genre: str) -> list[llm.Message]:
    return [
        llm.messages.system(
            "You are a conscientious librarian who talks like a pirate."
        ),
        llm.messages.user("Please recommend a book to me."),
        llm.messages.assistant(
            "Ahoy there, and greetings, matey! What manner of book be ye wantign?"
        ),
        llm.messages.user(f"I'd like a {genre} book, please."),
    ]


@llm.prompt()
def image_prompt(book_cover: llm.Image) -> list[llm.Content]:
    return ["What book is this?", book_cover]


@llm.prompt()
def videos_prompt(clips: list[llm.Video]) -> list[llm.Content]:
    return ["Do these video clips remind you of any book?", *clips]


@llm.prompt()
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
