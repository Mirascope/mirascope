from groq import Groq
from mirascope.core import BaseMessageParam, groq


@groq.call("llama-3.3-70b-versatile", client=Groq())
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
