from groq import AsyncGroq
from mirascope.core import groq


@groq.call("llama-3.3-70b-versatile", client=AsyncGroq())
async def recommend_book_async(genre: str) -> str:
    return f"Recommend a {genre} book"
