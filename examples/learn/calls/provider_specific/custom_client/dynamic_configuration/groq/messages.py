from groq import Groq
from mirascope.core import Messages, groq


@groq.call("llama-3.1-70b-versatile")
def recommend_book(genre: str) -> groq.GroqDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "client": Groq(),
    }
