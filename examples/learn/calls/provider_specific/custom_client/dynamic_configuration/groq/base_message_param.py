from groq import Groq
from mirascope.core import BaseMessageParam, groq


@groq.call("llama-3.3-70b-versatile")
def recommend_book(genre: str) -> groq.GroqDynamicConfig:
    return {
        "messages": [
            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
        ],
        "client": Groq(),
    }
