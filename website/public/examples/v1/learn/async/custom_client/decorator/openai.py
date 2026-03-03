from mirascope.core import openai
from openai import AsyncOpenAI # [!code highlight]


@openai.call("gpt-4o-mini", client=AsyncOpenAI()) # [!code highlight]
async def recommend_book_async(genre: str) -> str:
    return f"Recommend a {genre} book"
