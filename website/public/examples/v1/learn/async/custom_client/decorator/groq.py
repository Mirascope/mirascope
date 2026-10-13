from groq import AsyncGroq # [!code highlight]
from mirascope.core import groq


@groq.call("llama-3.1-70b-versatile", client=AsyncGroq()) # [!code highlight]
async def recommend_book_async(genre: str) -> str:
    return f"Recommend a {genre} book"
