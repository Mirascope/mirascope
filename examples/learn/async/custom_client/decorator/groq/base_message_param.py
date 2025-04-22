from groq import AsyncGroq
from mirascope.core import BaseMessageParam, groq


@groq.call("llama-3.3-70b-versatile", client=AsyncGroq())
async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
