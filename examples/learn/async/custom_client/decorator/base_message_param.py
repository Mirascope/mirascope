from mirascope import BaseMessageParam, llm
from openai import AsyncOpenAI


@llm.call(provider="openai", model="gpt-4o-mini", client=AsyncOpenAI())
async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
