from mirascope.core import openai
from openai import AsyncOpenAI


@openai.call("gpt-4o-mini", client=AsyncOpenAI())
async def recommend_book_async(genre: str) -> str:
    return f"Recommend a {genre} book"
