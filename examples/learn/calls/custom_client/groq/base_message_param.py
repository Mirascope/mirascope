from groq import Groq
from mirascope.core import BaseMessageParam, groq


@groq.call("llama-3.1-8b-instant", client=Groq())
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
