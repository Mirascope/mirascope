from google.generativeai import configure  # type: ignore

from mirascope.gemini import GeminiPrompt

configure(api_key="YOUR_GEMINI_API_KEY")


class BookRecommendation(GeminiPrompt):
    """
    USER:
    You're the world's greatest librarian.

    MODEL:
    Ok, I understand that I'm the world's greatest librarian. How can I help you?

    USER:
    Please recommend some {genre} books.
    """

    genre: str


prompt = BookRecommendation(genre="fantasy")
print(prompt.create())
