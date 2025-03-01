from mirascope import llm
from openai import AsyncOpenAI


@llm.call(provider="openai", model="gpt-4o-mini", client=AsyncOpenAI())
async def recommend_book_async(genre: str) -> str:
    return f"Recommend a {genre} book"
