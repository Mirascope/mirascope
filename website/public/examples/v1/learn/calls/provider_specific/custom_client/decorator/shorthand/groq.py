from groq import Groq # [!code highlight]
from mirascope.core import groq


@groq.call("llama-3.1-70b-versatile", client=Groq()) # [!code highlight]
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"
