from groq import Groq
from mirascope.core import groq


@groq.call("llama-3.1-8b-instant", client=Groq())
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"
