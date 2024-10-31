from mirascope.core import BaseMessageParam, openai
from openai import AsyncOpenAI


@openai.call("gpt-4o-mini", client=AsyncOpenAI())
async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
