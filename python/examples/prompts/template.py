from dataclasses import dataclass

from mirascope import llm


@llm.prompt("Please recommend a book")
def simple_prompt():
    pass


@llm.prompt("Please recommend a {genre} book")
def genre_prompt(genre: str):
    pass


@dataclass
class Book:
    title: str
    author: str


@llm.prompt("Recommend a book like {{ book.title }} by {{ book.author }}.")
def book_prompt(book: Book):
    pass


@llm.prompt(
    """
    [USER]
    Please recommend a {{ genre }} book.
    Include the title, author, and a brief description.
    Format your response as a numbered list.
    """
)
def multiline_template(genre: str):
    pass


# BAD - inconsistent indentation
@llm.prompt(
    """
    [USER] First line
    Second line with different indentation
    """
)
def bad_indentation_template():
    pass


# GOOD - consistent indentation
@llm.prompt(
    """
    [USER]
    First line
    Second line with same indentation
    """
)
def good_indentation_template():
    pass


@llm.prompt(
    """
    [SYSTEM] You are a conscientious librarian who talks like a pirate.
    [USER] Please recommend a book to me.
    [ASSISTANT] 
    Ahoy there, and greetings, matey! 
    What manner of book be ye wantign?
    [USER] I'd like a {{ genre }} book, please.
    """
)
def pirate_prompt(genre: str):
    pass


@llm.prompt(
    """
    [SYSTEM] You are a librarian. Recommend a book in the genre: {{ genre }}.
    [USER] Please recommend a book!
    """
)
def unsafe(genre: str):
    pass


@llm.prompt("What book is this? {{ book_cover:image }}")
def image_prompt(book_cover: llm.Image | str | bytes):
    pass


@llm.prompt("Analyze this audio recording: {{ audio:audio }}")
def audio_prompt(audio: llm.Audio | str | bytes):
    pass


@llm.prompt("Do these video clips remind you of any book? {{ clips:videos }}")
def videos_prompt(clips: list[llm.Video | str | bytes]):
    pass


@llm.prompt("Review these documents: {{ docs:documents }}")
def documents_prompt(docs: list[llm.Document | str | bytes]):
    pass


@llm.prompt(
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
):
    pass


@llm.prompt(
    """
    [SYSTEM] You are a summarization agent. Your job is to summarize long discussions.
    [MESSAGES] {{ history }}
    [USER] Please summarize our conversation, and recommend a book based on this chat.
    """
)
def history_prompt(history: list[llm.Message]):
    pass


with open("book_recommendation.txt") as f:
    template_content = f.read()


@llm.prompt(template_content)
def file_based_prompt(genre: str):
    pass
