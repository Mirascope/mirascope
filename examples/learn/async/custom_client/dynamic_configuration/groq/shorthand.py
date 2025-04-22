from groq import AsyncGroq
from mirascope.core import Messages, groq


@groq.call("llama-3.3-70b-versatile")
async def recommend_book(genre: str) -> groq.AsyncGroqDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "client": AsyncGroq(),
    }
