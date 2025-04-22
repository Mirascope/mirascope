from groq import Groq
from mirascope.core import groq


@groq.call("llama-3.3-70b-versatile", client=Groq())
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"
